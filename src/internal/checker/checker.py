import os
import sys
from urllib.parse import ParseResult
from .actions.block import contains_block

DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.join(DIR, "../..")
sys.path.append(os.path.abspath(ROOT_DIR))
sys.path.append(os.path.abspath(os.path.join(DIR, "../...")))

from database import db
from typing import NamedTuple
from components.singleton import Singleton
from collections import namedtuple
from .transaction import Transaction, CLIENT_REQUEST

SecurityAlert: NamedTuple = namedtuple("SecurityAlert", ["desc", "alert_on", "attack"])
     
class Checker(metaclass=Singleton):
    def __init__(self) -> None:
        self.sqli: set = db.load_signatures("sql_data.txt")
        self.xss: set = db.load_signatures("xss_data.txt")
        self.locations: set = db.load_signatures("locations.txt")        
    
    def check_transaction(self, tx: Transaction) -> bool:
        
        print(tx)
        
        path_check = self.__check_path(tx)
        sqli_check = self.__check_sql_injection(tx)
        xss_check = self.__check_xss(tx)
        
        return path_check or sqli_check or xss_check
    
    def contains_block(self, tx: Transaction) -> bool:
        return contains_block(tx)
    
    def __check_path(self, tx: Transaction) -> bool:
        """
        Checks if the resource that the transaction was made for is accessable.
        Accessable = inside the `locations.txt`.
        
        Questions:
        E.g the path: /admin/stats should be blocked?
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
        for _, values in tx.query_params.items():
            for value in values:
                s = {value.decode()}
                if bool(self.sqli.intersection(s)):
                    return True
        return False
    
    def __check_context(self, substring: str) -> None:
        """
        Checks if substring holds a payload that exists the outer context for SQLi.
        Exiting a context can start with: `'`
        Args:
            substring (str): part of a query.
        """
        
        # if `'` is present than the query might exit the context.
        # To ensure the querys validation the query MUST return the the context without injecting SQL payloads.
        # To check it we need to check for context esacping and if sql payload checks.
        # The payload `';-- DELETE users` will delete the table.
        
        # Context escaping characters.
        context_escaper = "'"
        for part in substring.split(context_escaper):
            for signature in self.sqli:
                if signature in part: 
                    sec_alert: NamedTuple = SecurityAlert(desc="Some fields containing SQLi signatures", alert_on=part, attack="SQL Injection")
                    return True, sec_alert
        return False
    
    def __check_xss(self, tx) -> None:
        pass
        