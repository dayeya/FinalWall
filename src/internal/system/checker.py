import os
import sys
from urllib.parse import ParseResult
from .actions.block import contains_block

DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.join(DIR, "../..")
sys.path.append(os.path.abspath(ROOT_DIR))
sys.path.append(os.path.abspath(os.path.join(DIR, "../...")))

from database import db
from typing import List, Tuple, Generator
from components.singleton import Singleton
from collections import namedtuple
from .transaction import Transaction, CLIENT_REQUEST
from .logging import AttackClassifier, SecurityLog, AccessLog, LogType


# CheckResult = [Malicious or not, A log object]
type CheckResult = Tuple[bool, LogType]


class Checker(metaclass=Singleton):
    def __init__(self) -> None:
        self.sqli: set = db.load_signatures("sql_data.txt")
        self.xss: set = db.load_signatures("xss_data.txt")
        self.locations: set = db.load_signatures("locations.txt")
    
    def check_transaction(self, tx: Transaction) -> CheckResult:
        """
        Checks `tx` for each attack and creates a log object (Can be either access or security).
        Returns: 
                CheckResult holding if the transaction is malicious or not, and the log object itself.
        """
        unauthorized, log = self.__check_path(tx)
        if unauthorized:
            return unauthorized, log
        sqli, log = self.__check_sql_injection(tx)
        if sqli:
            return sqli, log
        
        log = AccessLog(ip=tx.owner.ip, port=tx.owner.port, creation_date=tx.creation_date)
        return False, log

    def contains_block(self, tx: Transaction) -> bool:
        return contains_block(tx)
    
    def __check_path(self, tx: Transaction) -> CheckResult:
        """
        Checks if the resource that the transaction was made for is authorized.
        """
        log = None
        unauthorized_access = any({loc in tx.url.path for loc in self.locations})
        
        if unauthorized_access:
            log = SecurityLog(attack=AttackClassifier.UNAUTHORIZED_ACCESS, ip=tx.owner.ip, port=tx.owner.port, creation_date=tx.creation_date)
            return True, log
        return False, None
        
    def __check_sql_injection(self, tx: Transaction) -> CheckResult: 
        """
        Processes the transaction and finds any SQLnjection signatures.
        Can be found at place of the transaction.
        """
        for values in tx.query_params.values():
            for val in values:
                if any([signature in val for signature in self.sqli]):
                    log = SecurityLog(attack=AttackClassifier.SQL_INJECTION, ip=tx.owner.ip, port=tx.owner.port, creation_date=tx.creation_date)
                    return True, log
        return False, None
            
                    
    def __check_context(self, substring: str) -> CheckResult:
        """
        Checks if substring holds a payload that exists the outer context for SQLi.
        Exiting a context can start with: `'`
        Args:
            substring (str): part of a query.
        """
        
        # if `'` is present than the query might exit the context.
        # To ensure the querys validation the query MUST return the the context without injecting SQL payloads.
        # To check it we need to check for context esacping and if sql payload checks.
        # The payload `'; DELETE users` will delete the table.
        # O'Brian, 
        
        # Context escaping characters.
        context_escaper = "'"
        for part in substring.split(context_escaper):
            for signature in self.sqli:
                if signature in part:
                    return True, None
        return False, None
    
    def __check_xss(self, tx) -> None:
        return None, None
        