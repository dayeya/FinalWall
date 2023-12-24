"""
Author: Daniel Sapojnikov, 2023.
Blacklist Class.
"""

import toml
from pathlib import Path
from ..singleton.singleton import Singleton

EMPTY_BL = []
BLACKLIST_PATH = Path(__file__).parent.joinpath('blacklist.toml')

class BlackList(metaclass=Singleton):
    def __init__(self) -> None:
        self.__blacklist = set()
        self.__handler_path = Path(BLACKLIST_PATH)
        self.__initialize()

    @property
    def black_list(self) -> list:
        """Get the current blacklist."""
        return list(self.__blacklist)

    def __update_toml(self) -> None:
        """Update the TOML file with the current blacklist."""
        with self.__handler_path.open('w') as bl:
            toml.dump({'ip_blacklist': list(self.black_list)}, bl)
            
    def __initialize(self) -> None:
        """Load the blacklist from blacklist.toml"""
        open(self.__handler_path, 'w').close()
        with open(self.__handler_path, 'r') as bl:
            loaded = toml.load(bl)
        blacklisted = loaded.get('ip_blacklist', EMPTY_BL)
        self.__blacklist = set(blacklisted)
        self.__update_toml()

    def remove(self, ip: str) -> None:
        self.__blacklist.discard(ip)
        self.__update_toml()

    def add(self, ip: str) -> None:
        self.__blacklist.add(ip)
        self.__update_toml()