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
from httptools import HTTPSession

def sys_append_modules() -> None:
    """
    Appends all importent modules into sys_path.
    :returns: None.  
    """
    parent = '.../...'
    module = os.path.abspath(os.path.join(os.path.dirname(__file__), parent))
    sys.path.append(module)

sys_append_modules()
from common.network_object import (
    ServerConnection, 
    ClientConnection, 
    close_all
)
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
    def __init__(self, addr: Address, target: Address) -> None:
        self.__target = target
        self.__sessions: Dict[ClientConnection, HTTPSession] = {}
        self.__blacklist = BlackList()
        
        # Initialize BaseServer.
        super().__init__(addr, ADMIN)
        
    def __accept_client(self) -> ClientConnection:
        return ClientConnection(*self._main_sock.accept())
    
    def start(self) -> None:
        """
        Boots the proxy, waiting for clients.
        :returns: None.
        """
        print(f'[+] Picky started, address: {self._addr}')
        while True:
            client = self.__accept_client()
            print(f'[+] Logged a new client: {client.host_addr}')
            self.__handle_client(client)
    
    def __init_session(self, client: ClientConnection, server: ServerConnection) -> None:
        """
        Adds a HTTP session to sessions dict.
        """
        session = HTTPSession(client, server)
        self.__sessions[client] = session
    
    def __handle_client(self, client: ClientConnection) -> None:
        
        webserver_sock = socket(AF_INET, SOCK_STREAM)
        webserver_sock.connect(self.__target)
        
        web_server = ServerConnection(webserver_sock, self.__target)
        self.__init_session(client, web_server)
        
        current_session = self.__sessions[client]
        server_sock = current_session.get_server_sock()
        client_sock = current_session.get_client_sock()
    
        while True:
                
            request, _ = current_session.recv_full_http(from_server=False)
            safe_send(server_sock, request)
            
            if request:
                print(request)
                response, _ = current_session.recv_full_http(from_server=True)
                safe_send(client_sock, response)
            
            if not current_session.active():
                break
            
        current_session.close_session()
        del self.__sessions[client]

if __name__ == '__main__':
    waf = Proxy(addr=('127.0.0.1', 8080), target=('127.0.0.1', 50000))
    asyncio.run(waf.start())
