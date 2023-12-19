import os
import sys
import json
import asyncio
from base import BaseServer
from threading import Thread
from typing import Tuple, Union, Dict
from socket import socket, AF_INET, SOCK_STREAM
from components import BlackList
from httptools import HTTPSession
from httptools.errors import WebServerNotRunning

def sys_append_modules() -> None:
    """
    Appends all importent modules into sys_path.
    :returns: None.  
    """
    parent = '.../...'
    module = os.path.abspath(os.path.join(os.path.dirname(__file__), parent))
    sys.path.append(module)

sys_append_modules()
from config import load_config
from net.network_object.network_object import (
    ServerConnection,
    ClientConnection,
)
from net.aionetwork.aionetwork import (
    Address,
    create_new_task,
    safe_send
)

class Proxy(BaseServer):
    def __init__(self, addr: Address, target: Address, admin: Address) -> None:
        self.__target = target
        self.__blacklist = BlackList()
        self.__sessions: Dict[ClientConnection, HTTPSession] = {}
        
        # Initialize BaseServer.
        super().__init__(addr, admin)
        
    async def __accept_client(self) -> ClientConnection:
        """
        Waits for a client.
        :returns: ClientConnection.
        """
        loop = asyncio.get_event_loop()
        client, addr = await loop.sock_accept(self._main_sock)
        return ClientConnection(client, addr)
    
    async def start(self) -> None:
        print(f'[+] Blanket started, address: {self._addr}')
        
        while True:
            client = await self.__accept_client()
            print(f'[+] Logged a new client: {client.host_addr}')
            
            task: asyncio.Task = create_new_task(
                task_name=f'{client.host_addr} Handler', 
                task=self.__handle_client, 
                args=(client, ))
            await task
    
    def __add_session(self, client: ClientConnection, server: ServerConnection) -> None:
        session = HTTPSession(client, server)
        self.__sessions[client] = session
    
    async def connect_to_webserver(self) -> ServerConnection:
        sock = socket(AF_INET, SOCK_STREAM)
        try:
            sock.connect(self.__target)
            return ServerConnection(sock, self.__target)
        
        except ConnectionRefusedError:
            raise WebServerNotRunning(f'{self.__target} is not running.')
    
    async def __handle_client(self, client: ClientConnection) -> None:
        web_server = await self.connect_to_webserver()
        self.__add_session(client, web_server)
        
        current_session = self.__sessions[client]
        server_sock = current_session.server_sock
        client_sock = current_session.client_sock
        
        request = await current_session.recv_full_http(current_session.client_recv)
        await safe_send(server_sock, request)
        
        if request:
            response = await current_session.recv_full_http(current_session.server_recv)
            await safe_send(client_sock, response)
        
        if not current_session.active():
            return
            
        current_session.close_session()
        del self.__sessions[client]

if __name__ == '__main__':
    import stringtools
    print(stringtools.sum_as_string(1, 3))
    webserver, proxy, admin = load_config('network.toml') 
    waf = Proxy(addr=proxy, target=webserver, admin=admin)
    asyncio.run(waf.start())