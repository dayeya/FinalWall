from config import Config
from fmt_time import get_unix_time

import asyncio
from socket import socket, AF_INET, SOCK_STREAM
from src.proxy_network.behaviour import recv_from_client, forward_data, recv_from_server

from conversion import encode
from components import BlackList, Logger

from net.connection import Connection
from net.aionetwork import create_new_task, HostAddress

from internal.tokenization import tokenize
from internal.system.checker import Checker
from internal.database import SignaturesDB
from internal.system.actions.block import build_block, build_redirect
from internal.system.transaction import Transaction, SERVER_RESPONSE, CLIENT_REQUEST


class Waf:
    def __init__(self) -> None:
        self.config = Config()
        self.checker = Checker()
        self.logger = Logger("Waf")

        self.__address = self.config.proxy
        self.__address = self.__address["ip"], self.__address["port"]
        self.__sock = socket(AF_INET, SOCK_STREAM)
        self.__sock.bind(self.__address)
        self.__sock.listen()
        self.__sock.setblocking(False)

        self.logger.info(f"NetGuard running, {self.__address}")

    async def __accept_client(self) -> Connection:
        loop = asyncio.get_event_loop()
        client, addr = await loop.sock_accept(self.__sock)
        return Connection(client, HostAddress(*addr))

    async def __handle_connection(self, client: Connection) -> None:
        ip, port = self.config.webserver["ip"], self.config.webserver["port"]
        server = Connection(socket(AF_INET, SOCK_STREAM), HostAddress(ip, port))
        await server.establish()
        request, err = await recv_from_client(client)
        if err:
            self.logger.error(f"Failed request.")

        # real_host_address and has_proxies are evaluated at inspection time.
        tx = Transaction(
            owner=client.addr,
            real_host_address=None,
            has_proxies=False,
            raw=request,
            side=CLIENT_REQUEST,
            creation_date=get_unix_time()
        )
        tx.process()

        valid_transaction, log_object = await self.checker.check_transaction(tx)
        if valid_transaction:
            token = tokenize()
            location = encode("/block?token=" + token)
            redirection = build_redirect(location)
            await forward_data(client, redirection)
            print(log_object)

        elif token := self.checker.contains_block(tx):
            block_html: bytes = build_block(token)
            await forward_data(client, block_html)

        else:
            print(log_object)
            await forward_data(server, request)
            response, err = await recv_from_server(server)
            if err:
                self.logger.error(f"Failed recv.")
            await forward_data(client, response)

    async def start(self) -> None:
        while True:
            client = await self.__accept_client()
            task = create_new_task(
                task_name=f"HANDLE_CONNECTION({client.addr})",
                task=self.__handle_connection,
                args=(client,),
            )
            await task


async def main():
    try:
        SignaturesDB()
    except Exception as _database_loading_err:
        print("ERROR: Could not initialize database due:", _database_loading_err)
    waf = Waf()
    await waf.start()

if __name__ == "__main__":
    import tracemalloc

    tracemalloc.start()
    asyncio.run(main())
