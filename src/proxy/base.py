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
from net.aionetwork.aionetwork import Address

class BaseServer:
    """
    BaseServer defines the basic configuration of the Picky proxy.
    """
    def __init__(self, addr: Address, admin: Address) -> None:
        self._addr = addr
        self._admin = admin

        self.__create_socks()
        self.__establish_socks()
        
        self._main_sock.listen()
        self._main_sock.setblocking(False)
    
    def __create_socks(self) -> None:
        self._main_sock  = socket(AF_INET, SOCK_STREAM)
        self._admin_sock = socket(AF_INET, SOCK_STREAM)
        
    def __establish_socks(self) -> None:
        """
        Establishes connections or bindings for all needed sockets.
        """
        self._main_sock.bind(self._addr)