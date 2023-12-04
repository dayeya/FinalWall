"""
Author: Daniel Sapojnikov 2023.
Reverse proxy module of the Picky System.
"""
import os
import sys
# import argparse
import asyncio
# from threading import Thread
# from http_service import HTTPService
from typing import Tuple, Union, Dict
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

NetworkObject = Union[Client, socket]

def close_all(*args: Tuple[NetworkObject]) -> None:
    """
    NetworkObject: Client or a Socket.
    Closes all network objects.
    """
    for obj in args:
        classify = obj.__class__.__name__
        try:
            with getattr(obj, 'close', None):           
                print(f'[!] A {classify} object was closed successfuly!')
        except Exception as close_error:
            print(f'[!] {classify}.close() was not complete. {close_error}')

class Proxy(BaseServer):
    """
    Proxy class for Picky.
    """
    def __init__(self, addr: Address=(loop_back, 8080), admin: Address=(loop_back, 50000)) -> None:
        """
        Basic __init__ function.
        """
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
            self.__handle_client(self.__accept_client())
            
    def __handle_client(self, client: Client) -> None:
        """
        Handles a single request in an asynchronous manner.
        """
        print(f'[+] Logged a new client: {client.addr}')
        request, result = safe_recv(client.sock, buffer_size=8192)
        
        if not result: 
            client.close()
            return
        
        print('Request', request)
        webserver_sock = socket(AF_INET, SOCK_STREAM)
        webserver_sock.connect(('127.0.0.1', 80))
        
        safe_send(webserver_sock, request)
        
        response, result = safe_recv(webserver_sock, buffer_size=8192)
        if not result:
            close_all(webserver_sock, client)
            return
        
        print('Response', response) 
        safe_send(client.sock, response)
        
        close_all(webserver_sock, client)

if __name__ == '__main__':
    waf = Proxy()
    asyncio.run(waf.start())
