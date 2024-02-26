import os
import sys
from .actions.block import contains_block

DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.join(DIR, "../..")
sys.path.append(os.path.abspath(ROOT_DIR))
sys.path.append(os.path.abspath(os.path.join(DIR, "../...")))

from database import db
from http_tools import path_segment
from components.singleton import Singleton

class RequestChecker(metaclass=Singleton):
    def __init__(self) -> None:
        self.sqli = db.load_signatures("sql_data.txt")
        self.xss = db.load_signatures("xss_data.txt")
        self.locations = db.load_signatures("locations.txt")
    
    def check_request(self, request: bytes) -> bool:
        return self.__check_forbidden_location(request)
    
    def contains_block(self, request: bytes) -> bool:
        return contains_block(request)
    
    def __check_forbidden_location(self, request: bytes) -> bool:
        _method, requested_location = path_segment(str(request))
        common = self.locations.intersection({requested_location})
        return requested_location in self.locations
        
    def __check_sql(self) -> None: 
        pass
    
    def __check_xss(self) -> None:
        pass
        