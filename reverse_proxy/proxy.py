"""
Author: Daniel Sapojnikov 2023.
Reverse proxy module of the Picky System.
"""
import os
import sys
import argparse
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from typing import Tuple

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
from common.network import all_interfaces, listen_bound, loop_back
from common.network import create_new_thread, safe_send, safe_recv

Address = Tuple[str, int]

class Proxy:
    def __init__(self, addr: Address=(all_interfaces, 8080), admin: Address=(loop_back, 50000)) -> None:
        """
        Creates a proxy object.
        :params: addr - tuple[str, int], optional).
        :returns: None.
        """
        self.__admin = admin
        self.__ip, self.__port = addr
        self.__configure_socks()
        self.__connect_socks()
        
        # Start listening.
        self.__main_sock.listen(listen_bound) # Check possible flaw
        
    def __configure_socks(self) -> None:
        """
        Initializes the connection to all interfaces.
        :returns: None.
        """
        self.__main_sock  = socket(AF_INET, SOCK_STREAM)
        self.__admin_sock = socket(AF_INET, SOCK_STREAM)
        
    def __connect_socks(self) -> None:
        """
        Connects all sockets to specific destinations.
        """
        self.__main_sock.bind((self.__ip, self.__port))
        self.__admin_sock.connect(self.__admin)
        
    def __accept_client(self) -> Client:
        """
        Accepts a client.
        :returns: A client object.
        """
        return Client(*self.__main_sock.accept())
    
    def __boot_proxy(self) -> None:
        """
        Boots the proxy, waiting for clients.
        :returns: None.
        """
        print(f'[+] Picky started, address_{self.__ip}:{self.__port}')
        while True:
            client = self.__accept_client()
            print(f'[+] Logged a new client: {client.addr}')
            
            # Create thread and start it.
            thread: Thread = create_new_thread(self.__handle_client, client)
            thread.start()
            
    def __handle_client(self, client: Client) -> None:
        """
        Handles all HTTP traffic from client.
        """
        while True:
            data = safe_recv(client.sock, buffer_size=4096)
            if not data: break
            print(f'[+] Data recieved: {data}')
            safe_send(client.sock, f'echo: {data}')
            
        # End communication with client.
        client.close()
          
    def start(self) -> None:
        """
        Boots the proxy.
        """
        self.__boot_proxy()
            
        
if __name__ == '__main__':
    waf = Proxy()
    waf.start()
