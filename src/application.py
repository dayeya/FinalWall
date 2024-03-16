import asyncio
from proxy.proxy import Proxy
from net.aionetwork import create_new_task

import asyncio
from config import Config
from conversion import encode
from socket import socket, AF_INET, SOCK_STREAM
from components import BlackList, Logger
from net.connection import Connection
from internal.checker.transaction import Transaction, SERVER_RESPONSE, CLIENT_REQUEST
from internal.tokenization import tokenize 
from internal.checker.checker import Checker
from internal.checker.actions.block import build_block, build_redirect


class Waf:
    def __init__(self) -> None:
        self.cnf = Config()
        self.proxy = Proxy()
        self.checker: Checker = Checker()
        self.logger = Logger("Waf")
        
        address = self.cnf["Proxy"]
        self.__sock = socket(AF_INET, SOCK_STREAM)
        self.__sock.bind(address)
        self.__sock.listen()
        self.__sock.setblocking(False)
        
        self.logger.info(f"NetGuard running, {address}")
    
    async def __accept_client(self) -> Connection:
        loop = asyncio.get_event_loop()
        client, addr = await loop.sock_accept(self.__sock)
        return Connection(client, addr)
    
    def __new_transaction(self, data: bytes, side: int) -> Transaction:
        return Transaction(data, side)
    
    async def __wire_new_connection(self) -> Connection:
        try:
            loop = asyncio.get_event_loop()
            server_address: tuple = self.cnf["Server"]
            sock = socket(AF_INET, SOCK_STREAM)
            await loop.sock_connect(sock, server_address)
            return Connection(sock, server_address)
            
        except OSError as e:
            self.logger.error(f"Connection error, {e}")
            return
    
    async def __handle_connection(self, client: Connection) -> None:
        
        server = await self.__wire_new_connection()
        request, err = await self.proxy.recv_from_client(client)
        if err:
            self.logger.error(f"Failed request.")
            
        tx = self.__new_transaction(request, CLIENT_REQUEST)
        tx.process()    
        
        # Check for malicious transaction.
        malicious_transaction = self.checker.check_transaction(tx)
        if malicious_transaction:
            token = tokenize()
            location = encode("/block?token=" + token)
            redirection = build_redirect(location)
            await self.proxy.forward_data(client, redirection)
            
            # Update Security log.

        # GET for security page.
        elif token := self.checker.contains_block(tx):
            block_html = build_block(token)
            await self.proxy.forward_data(client, block_html)
            
            # Update Security log.
        
        # Valid transaction.
        else:
            await self.proxy.forward_data(server, request)
            response, err = await self.proxy.recv_from_server(server)
            if err:
                self.logger.error(f"Failed recv.")
            await self.proxy.forward_data(client, response)
            
            # Update Access log.
            
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
    waf = Waf()
    asyncio.run(waf.start())
    