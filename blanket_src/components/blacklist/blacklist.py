"""
Author: Daniel Sapojnikov, 2023.
Blacklist Class.
"""
import toml
import tomllib

BLACKLIST_PATH = 'blacklist_test/blacklist.toml'

class BlackList:
    def __init__(self) -> None:
        self.__blacklist = set()
        self.__handler_path = BLACKLIST_PATH
        
        # Create a toml file, and push default dict to it.
        with open(self.__handler_path, 'w') as bl:
            toml.dump({'ip_blacklist': []}, bl)
    
    @property
    def black_list(self) -> list:
        return list(self.__blacklist)
    
    def __contains__(self, ip: str) -> bool:
        return ip in self.__blacklist 
    
    def __update_toml(self) -> None:
        with open(self.__handler_path, 'w') as bl:
            toml_str = toml.dumps({'ip_blacklist': self.black_list})
            bl.write(toml_str)
    
    def remove(self, ip: str) -> None:
        self.__blacklist.remove(ip)
        self.__update_toml()
            
    def add(self, ip: str) -> None:
        self.__blacklist.add(ip)
        self.__update_toml()
            
if __name__ == '__main__':
    bl = BlackList()
    bl.add('192.168.1.1')