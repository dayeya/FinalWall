from threading import Thread
from typing import List, Dict, Tuple, Any, Union

class Proxy:
    
    def __init__(self, addr: tuple[str, int]=('localhost', 60000)) -> None:
        """
        Creates a Proxy at addr.

        Args:
            addr (tuple[str, int], optional): Location. Defaults to ('localhost', 60000).
        """
        self.__addr = addr
    
    def boot_proxy(self) -> None:
        """
        Boots proxy, listening to traffic.
        """ 