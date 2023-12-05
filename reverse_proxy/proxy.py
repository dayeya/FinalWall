"""
Author: Daniel Sapojnikov 2023.
Reverse proxy module of the Picky System.
"""
import os
import sys
import asyncio
import argparse
from base import BaseServer
from threading import Thread
from typing import Tuple, Union, Dict
from socket import socket, AF_INET, SOCK_STREAM
from components import BlackList
from http_handling import recv_http 

def sys_append_modules() -> None:
    """
    Appends all importent modules into sys_path.
    :returns: None.  
    """
    parent = '.../...'
    module = os.path.abspath(os.path.join(os.path.dirname(__file__), parent))
    sys.path.append(module)

sys_append_modules()
from common.network_object import Client, close_all
from common.network import (
    null_ip, 
    loop_back,
    Address,
    create_new_thread, 
    safe_send, 
    safe_recv
)

# Add admin addr.
ADMIN = ()

class Proxy(BaseServer):
    """
    Proxy class for Picky.
    """
    def __init__(self, 
            addr: Address, 
            target: Address
        ) -> None:
        """
        Basic __init__ function.
        """
        self.__target = target
        self.__blacklist = BlackList()
        super().__init__(addr, ADMIN)
        
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
    
    def __handle_client(self, client: Client) -> None:
        
        webserver_sock = socket(AF_INET, SOCK_STREAM)
        webserver_sock.connect(self.__target)
        
        while True:
            request, result = safe_recv(client.sock, buffer_size=8192)
            if not result: 
                break

            safe_send(webserver_sock, request)

            data, result = recv_http(webserver_sock)
            if not result:
                break
            safe_send(client.sock, data)
            
        close_all(webserver_sock, client)

if __name__ == '__main__':
    waf = Proxy(addr=('127.0.0.1', 8080), target=('127.0.0.1', 80))
    asyncio.run(waf.start())
