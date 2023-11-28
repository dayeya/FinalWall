import os
import sys
from socket import *
from threading import Thread
from typing import List, Dict, Tuple, Any, Union

def sys_append_modules():
    """
    Appends all importent modules into sys_path.
    :returns: None. 
    """
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../...'))
    sys.path.append(parent_dir)

sys_append_modules()
from util_modules.network_client import Client
from util_modules.network import create_new_thread, safe_send, safe_recv
from util_modules.network import all_interfaces, listen_bound

Address = Tuple[str, int]

class Proxy:
    def __init__(self, addr: Address=(all_interfaces, 60000)) -> None:
        """
        Creates a proxy object.
        :params: addr - tuple[str, int], optional).
        :returns: None.
        """
        self.__ip, self.__port = addr
        self.__main_sock = socket(AF_INET, SOCK_STREAM)
        self.__configure_socket()

    @property
    def main_sock(self) -> socket:
        """
        Getter for the main socket.
        :returns: socet object.
        """
        return self.__main_sock
        
    def __configure_socket(self) -> None:
        """
        Initializes the connection to all interfaces. 
        :returns: None.
        """
        self.__main_sock.bind((self.__ip, self.__port))
        self.__main_sock.listen(listen_bound)
        
    def __accept_client(self) -> Client:
        """
        Waits for a client, return a new Client.

        Returns:
            Client: Client object of the accepeted end-point.
        """
        return Client(*self.__main_sock.accept())
    
    def __boot_proxy(self) -> None:
        """
        Boots the proxy, waiting for clients.
        :returns: None.
        """
        print(f'[+] Started proxy!')
        while True:
            client = self.__accept_client()
            print(f'[+] Logged a new client, {client}')
            
            # Create thread and start it.
            thread: Thread = create_new_thread(self.__handle_client, client)
            thread.start()
            
    def __handle_client(self, client: Client) -> None:
        while True:
            data = safe_recv(client.sock)
            if not data: break
            print(f'[+] Data recieved: {data}')
            safe_send(client.sock, f'ECHO: {data}')
            
        # End communication with client.
        client.close()
          
    def start(self) -> None:
        self.__boot_proxy()
            
        
if __name__ == '__main__':
    waf = Proxy()
    waf.start()