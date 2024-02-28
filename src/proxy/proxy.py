import asyncio
from typing import Dict
from base import BaseServer
from config import load_config
from http_session import HTTPSession
from socket import socket, AF_INET, SOCK_STREAM
from components import BlackList, Logger, PROXY_LOGGER
from net.aionetwork import create_new_task, Address
from conversion import encode
from net.network_object import ServerConnection, ClientConnection
from internal.tokenization import tokenize 
from internal.request_checker.checker import RequestChecker
from internal.request_checker.actions.block import build_block, build_redirect

class Proxy(BaseServer):
    def __init__(self, addr: Address, target: Address, admin: Address) -> None:
        super().__init__(addr, admin)
        self.__target = target
        self.logger: Logger = Logger(PROXY_LOGGER)
        self.sessions: Dict[HTTPSession, bool] = {}
        self.checker: RequestChecker = RequestChecker()

    async def __accept_client(self) -> ClientConnection:
        loop = asyncio.get_event_loop()
        client, addr = await loop.sock_accept(self._main_sock)
        return ClientConnection(client, addr)

    async def __init_server_connection(self) -> ServerConnection:
        try:
            sock = socket(AF_INET, SOCK_STREAM)
            sock.connect(self.__target)
            return ServerConnection(sock, self.__target)
        except ConnectionRefusedError:
            self.logger.error(f"{self.__target} is not running.")

    async def __handle_connection(self, client: ClientConnection) -> None:
        http_session = HTTPSession(client, await self.__init_server_connection(), self._addr)
        request, err = await http_session.client_recv()
        if err:
            self.logger.error(f"Could not recv any data from client: {http_session.client_addr}")
        
        # Check for malicious input.
        if self.checker.check_request(request):
            token = tokenize()
            location = encode("/block?token=" + token)
            redirection = build_redirect(location)
            await http_session.send_to_client(redirection)

        # GET for security page.
        elif token := self.checker.contains_block(request):
            block_html = build_block(token)
            await http_session.send_to_client(block_html)
        
        # Valid input.
        else:
            await http_session.send_to_server(request)
            response, err = await http_session.server_recv()
            if err:
                self.logger.error(f"Could not recv any data from server: {http_session.server_addr}")
            print(response)
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