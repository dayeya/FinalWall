"""
Author: Daniel Sapojnikov 2023.
Reverse proxy module of the Picky System.
"""
import os
import sys
# import argparse
import asyncio
# from threading import Thread
from http_service import HTTPService
from base import BaseServer
from blacklist import BlackList
from socket import socket, AF_INET, SOCK_STREAM 

def sys_append_modules() -> None:
    """
    Appends all importent modules into sys_path.
    :returns: None.  
    """
    parent = '../...'
    module = os.path.abspath(os.path.join(os.path.dirname(__file__), parent))
    sys.path.append(module)

sys_append_modules()
from common.network_client import Client
from common.network import (
    null_ip, 
    loop_back,
    Address,
    create_new_thread, 
    safe_send, 
    safe_recv 
)

class Proxy(BaseServer):
    """
    Proxy class, provides a service of communication between 2 endpoints.
    """
    def __init__(
            self, 
            addr: Address=(loop_back, 8080), 
            admin: Address=(loop_back, 50000),
        ) -> None:
        
        # All needed assets.
        self.__web_server = socket(AF_INET, SOCK_STREAM)
        self.__blacklist = BlackList()
        super().__init__(addr, admin)
        
    def __accept_client(self) -> Client:
        return Client(*self._main_sock.accept())
    
    def start(self) -> None:
        """
        Boots the proxy, waiting for clients.
        :returns: None.
        """
        print(f'[+] Picky started, address: {self._addr}')
        while True:
            client = self.__accept_client()
            print(f'[+] Logged a new client: {client.addr}')
            self.__handle_client(client)

    def recv_http(self) -> None:
        pass
    
    def forward_http(self) -> None:
        pass
    
    def __handle_client(self, client: Client) -> None:
        """
        Handles a single request in a asynchronious manner.
        """
        request, result = safe_recv(client.sock, buffer_size=8192)
        
        # Check for abortion problems.
        if not result: 
            client.close()
        
        webserver_sock = socket(AF_INET, SOCK_STREAM)
        webserver_sock.connect(('127.0.0.1', 50000))
        
        safe_send(webserver_sock, request)
        
        response, result = safe_recv(webserver_sock, buffer_size=8192)
        if not result:
            webserver_sock.close()
        
        print(response) 
        safe_send(client.sock, response)
        
        webserver_sock.close()
        client.close()

if __name__ == '__main__':
    waf = Proxy()
    asyncio.run(waf.start())
