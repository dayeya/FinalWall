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
from .transaction import Transaction, CLIENT_REQUEST
from http_tools.tools import SearchContext, search_header


URL_PARAM_PREFIX = "?"
URL_PARAM_SPERATOR = "&"
URL_PARAM_EQUALS = "="
                
class RequestChecker(metaclass=Singleton):
    def __init__(self) -> None:
        self.sqli = db.load_signatures("sql_data.txt")
        self.xss = db.load_signatures("xss_data.txt")
        self.locations = db.load_signatures("locations.txt")
    
    def check_request(self, request: bytes) -> bool:
        
        # Create a transaction.
        tx = Transaction(request, CLIENT_REQUEST)
        tx.process()
        
        print(tx)
        
        return self.__check_forbidden_uri(tx)
    
    def contains_block(self, request: bytes) -> bool:
        return contains_block(request)
    
    def __check_forbidden_uri(self, tx: Transaction) -> bool:
        uri = tx.uri.decode()
        common = self.locations.intersection({uri})
        return bool(common)
        
    def __check_sql(self) -> None: 
        pass
    
    def __check_xss(self) -> None:
        pass
        