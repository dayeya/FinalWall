"""
Author: Daniel Sapojnikov, 2023.
Blacklist Class.
"""

from .singleton import Singleton

class BlackList(metaclass=Singleton):
    """
    Blacklist class used to handle blacklisted ip's.
    """
    def __init__(self) -> None:
        self.__blacklist = set()
        
    def __contains__(self, ip: str) -> bool:
        """
        Checks if 'ip' is in the blacklist.
        :returns: Bool.
        """
        return ip in self.__blacklist
    
    def remove(self, ip: str) -> None:
        pass
    
    def add(self, ip: str) -> None:
        pass