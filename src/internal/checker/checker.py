import os
import sys
from urllib.parse import ParseResult
from .actions.block import contains_block

DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.join(DIR, "../..")
sys.path.append(os.path.abspath(ROOT_DIR))
sys.path.append(os.path.abspath(os.path.join(DIR, "../...")))

from database import db
from components.singleton import Singleton
from .transaction import Transaction, CLIENT_REQUEST
from http_tools.tools import SearchContext, search_header

                
class Checker(metaclass=Singleton):
    def __init__(self) -> None:
        self.sqli = db.load_signatures("sql_data.txt")
        self.xss = db.load_signatures("xss_data.txt")
        self.locations = db.load_signatures("locations.txt")
    
    def check_transaction(self, tx: Transaction) -> bool:
        return self.__check_forbidden_uri(tx)
    
    def contains_block(self, tx: Transaction) -> bool:
        return contains_block(tx)
    
    def __check_forbidden_uri(self, tx: Transaction) -> bool:
        """
        Checks if the resource that the transaction was made for is accessable.
        Accessable = inside the `locations.txt`.
        """
        path = tx.url.path.decode()
        common = self.locations.intersection({path})
        return bool(common)
        
    def __check_sql_injection(self, tx: Transaction) -> bool: 
        """
        Processes the transaction and finds any SQL Injection signatures.
        Can be found at place of the transaction.
        """
        
        # What if an SQL keyword appears at the URI location?
        
        # Check for SQL keywords in the parameters.
        for field_name, field_value in tx.params.items():
            fields_set = {field_name, field_value}
            if fields_set.intersection(self.sqli):
                return True
        return False
    
    def __check_xss(self) -> None:
        pass
        