from socket import *
from threading import Thread
from typing import List, Dict, Tuple, Any, Union

from util_modules import UNIVERSAL_IP
from simple_client import SimpleClient

PORT = 60000
class Proxy:
    
    def __init__(self, addr: tuple[str, int]=('localhost', 60000)) -> None:
        """
        Creates a Proxy at addr.

        Args:
            addr (tuple[str, int], optional): Location. Defaults to ('localhost', 60000).
        """
        self.__addr = addr
        self.__main_sock = socket(AF_INET, SOCK_STREAM)
        
    def __accept_client(self) -> SimpleClient:
        """
        Waits for a client, return a new SimpleClient.

        Returns:
            SimpleClient: Client object of the accepeted end point.
        """
        return SimpleClient(self.__main_sock.accept())