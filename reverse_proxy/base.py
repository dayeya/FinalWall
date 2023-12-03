import os
import sys
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
from common.network import Address

class BaseServer:
    """
    Base class for a proxy server.
    """
    def __init__(self, addr: Address, admin: Address) -> None:
        self.__addr = addr
        self.__admin = admin
        
        # setup all needed sockets.
        self.__create_socks()
        self.__establish_socks()
        
        self.__main_sock.listen()
    
    def __create_socks(self) -> None:
        self.__main_sock  = socket(AF_INET, SOCK_STREAM)
        self.__admin_sock = socket(AF_INET, SOCK_STREAM)
        
    def __establish_socks(self) -> None:
        """
        Establishes all needed sockets.
        """
        self.__main_sock.bind(self.__addr)