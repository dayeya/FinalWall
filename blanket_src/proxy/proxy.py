import asyncio
from typing import Dict
from base import BaseServer
from config import load_config
from http_session import HTTPSession
from socket import socket, AF_INET, SOCK_STREAM

from components import BlackList, Logger, PROXY_LOGGER
from net.network_object import (
    ServerConnection,
    ClientConnection
)
from net.aionetwork import Address, safe_send, create_new_task


class Proxy(BaseServer):
    def __init__(self, addr: Address, target: Address, admin: Address) -> None:
        super().__init__(addr, admin)

        self.__target = target
        self.__blacklist = BlackList()
        self.__logger = Logger(PROXY_LOGGER)
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
            print(ConnectionRefusedError(f"{self.__target} is not running."))

    async def __handle_client(self, client: ClientConnection) -> None:
        web_server = await self.__connect_to_webserver()
        self.__add_session(client, web_server)

        current_session = self.__sessions[client]
        server_sock = current_session.server_sock
        client_sock = current_session.client_sock

        request, _ = await current_session.client_recv()
        await safe_send(server_sock, request)

        if request:
            
            # Check for forbidden words. 
            # if (contains_forbidden_words(request)):
            
            response, _ = await current_session.server_recv()
            await safe_send(client_sock, response)

        if not current_session.active():
            return

        current_session.close_session()
        del self.__sessions[client]

    async def start(self) -> None:
        self.__logger.log_date(f"Blanket started, address: {self._addr}")
        while True:
            client = await self.__accept_client()

            task: asyncio.Task = create_new_task(
                task_name=f"{client.host_addr} Handler",
                task=self.__handle_client,
                args=(client,),
            )
            await task


if __name__ == "__main__":
    webserver, proxy, admin = load_config("network.toml")
    waf = Proxy(addr=proxy, target=webserver, admin=admin)
    asyncio.run(waf.start())
