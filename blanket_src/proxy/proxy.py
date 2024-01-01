import asyncio
from typing import Dict
from base import BaseServer
from config import load_config
from http_session import HTTPSession
from socket import socket, AF_INET, SOCK_STREAM
from components import BlackList, Logger, PROXY_LOGGER
from net.aionetwork import create_new_task, Address

from net.network_object import (
    ServerConnection,
    ClientConnection

)
from conversion import encode
from internal.gentoken import tokenize 
from internal.analyze.access import contains_forbidden_paths
from actions.block import build_block, build_redirect, has_block

class Proxy(BaseServer):
    def __init__(self, addr: Address, target: Address, admin: Address) -> None:
        super().__init__(addr, admin)

        self.__target = target
        self.__blacklist = BlackList()
        self.logger = Logger(PROXY_LOGGER)
        self.__sessions: Dict[ClientConnection, HTTPSession] = {}

    async def __accept_client(self) -> ClientConnection:
        loop = asyncio.get_event_loop()
        client, addr = await loop.sock_accept(self._main_sock)
        return ClientConnection(client, addr)

    def __add_session(self, client: ClientConnection, server: ServerConnection) -> None:
        session = HTTPSession(client, server, self._addr)
        self.__sessions[client] = session

    async def __connect_to_webserver(self) -> ServerConnection:
        try:
            sock = socket(AF_INET, SOCK_STREAM)
            sock.connect(self.__target)
            return ServerConnection(sock, self.__target)

        except ConnectionRefusedError:
            self.logger.error(f"{self.__target} is not running.")

    async def __handle_connection(self, client: ClientConnection) -> None:
        """
        Simple function to handle single TCP connection.
        """
        blocked = False
        http_session = HTTPSession(client, await self.__connect_to_webserver(), self._addr)
        request, err = await http_session.client_recv()
        if err:
            self.logger.error(f"Could not recv any data from client: {http_session.client_addr}")
        
        # Check for malicious input.
        if contains_forbidden_paths(request):
            token = tokenize()
            location = encode("/block?token=" + token)
            redirection = build_redirect(location)
            print(redirection)
            await http_session.send_to_client(redirection)

        # GET for security page.
        if token := has_block(request):
            blocked = True
            print(token)
            block_html = build_block(token)
            await http_session.send_to_client(block_html)
        
        # Valid input.
        if not blocked:
            await http_session.send_to_server(request)
            response, err = await http_session.server_recv()
            if err:
                self.logger.error(f"Could not recv any data from server: {http_session.server_addr}")
            await http_session.send_to_client(response)

    async def start(self) -> None:
        while True:
            client = await self.__accept_client()
            task = create_new_task(
                task_name=f"{client.host_addr} Handler",
                task=self.__handle_connection,
                args=(client,),
            )
            await task

if __name__ == "__main__":
    webserver, proxy, admin = load_config("network.toml")
    waf = Proxy(addr=proxy, target=webserver, admin=admin)
    asyncio.run(waf.start())