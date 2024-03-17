from config import Config
from fmt_time import get_unix_time

import asyncio
from proxy.proxy import Proxy
from socket import socket, AF_INET, SOCK_STREAM

from conversion import encode
from components import BlackList, Logger

from net.connection import Connection
from net.aionetwork import create_new_task, Address

from internal.tokenization import tokenize 
from internal.system.checker import Checker
from internal.system.actions.block import build_block, build_redirect
from internal.system.transaction import Transaction, SERVER_RESPONSE, CLIENT_REQUEST


# TODO: Manage sessions for each client.

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
        return Connection(client, Address(*addr))
    
    def __new_transaction(self, owner: Address, data: bytes, side: int, creation_date) -> Transaction:
        return Transaction(owner=owner, creation_date=creation_date, raw=data, side=side)
    
    async def __wire_new_connection(self) -> Connection:
        """
        Creats a new `Connection` to the web server to handle each TCP stream.
        Returns: 
                Connection object.
        """
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
        
        tx = self.__new_transaction(client.address, request, CLIENT_REQUEST, creation_date=get_unix_time())
        tx.process()
        
        print(tx)
        
        # Check for malicious transaction.
        valid_transaction, log_object = self.checker.check_transaction(tx)
        if valid_transaction:
            token = tokenize()
            location = encode("/block?token=" + token)
            redirection = build_redirect(location)
            await self.proxy.forward_data(client, redirection)
            
            # Log the alert (Security log)
            print(log_object)

        # GET for security page.
        elif token := self.checker.contains_block(tx):
            block_html = build_block(token)
            await self.proxy.forward_data(client, block_html)
        
        # Valid transaction.
        else:
            print(log_object)
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
    