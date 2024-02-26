import os
import sys
import urllib.parse
from .actions.block import contains_block

DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.join(DIR, "../..")
sys.path.append(os.path.abspath(ROOT_DIR))
sys.path.append(os.path.abspath(os.path.join(DIR, "../...")))

from database import db
from components.singleton import Singleton
from http_tools import path_segment, get_host


URL_PARAM_PREFIX = "?"
URL_PARAM_SPERATOR = "&"
URL_PARAM_EQUALS = "="


class RequestNormalisation:
    def __init__(self) -> None:
        self.method: str = ""
        self.location: str = ""
        self.query_params: dict = {}
        self.query_len: int = 0
    
    def fold(self, request: bytes) -> None:
        """
        Inspects the query params and requested locations inside request.
        Return: 
            Tuple[Str, Dict] = (Location, Params)
        """
        request = str(request)
        partial_url: str = ""
        query_data: str = ""
        method, partial_url = path_segment(request)
        self.method = method
        
        # Check for query parameters.
        if partial_url.find(URL_PARAM_PREFIX) != -1:
            self.location, query_data = partial_url.split(URL_PARAM_PREFIX)
            for key, value in [data.split(URL_PARAM_EQUALS) for data in query_data.split(URL_PARAM_SPERATOR)]:
                self.query_params[key] = value 
            self.query_len = len(self.query_params)
        
        # No query parameters.
        # TODO: Support POST method.
        else:
            self.location = partial_url
            
    
    def format(self) -> str:
        return f"{self.method},{self.location},{self.query_params},{self.query_len}"
                
class RequestChecker(metaclass=Singleton):
    def __init__(self) -> None:
        self.sqli = db.load_signatures("sql_data.txt")
        self.xss = db.load_signatures("xss_data.txt")
        self.locations = db.load_signatures("locations.txt")
    
    def check_request(self, request: bytes) -> bool:
        norm = RequestNormalisation()
        norm.fold(request)
        print(norm.format())
        return self.__check_forbidden_location(norm)
    
    def contains_block(self, request: bytes) -> bool:
        return contains_block(request)
    
    def __check_forbidden_location(self, request: RequestNormalisation) -> bool:
        common = self.locations.intersection({request.location})
        return bool(common)
        
    def __check_sql(self) -> None: 
        pass
    
    def __check_xss(self) -> None:
        pass
        