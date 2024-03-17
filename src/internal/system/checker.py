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
from .logging import SecurityLog, AccessLog, LogType


# CheckResult = [Malicious or not, A log object]
type CheckResult = Tuple[bool, List[LogType]]


class Checker(metaclass=Singleton):
    def __init__(self) -> None:
        self.sqli: Generator = db.load_signatures("sql_data.txt")
        self.xss: Generator = db.load_signatures("xss_data.txt")
        self.locations: set = set(db.load_signatures("locations.txt"))        
    
    def check_transaction(self, tx: Transaction) -> CheckResult:
        """
        Checks `tx` for each attack and creates a log object (Can be either access or security).
        Returns: 
                CheckResult holding if the transaction is malicious or not, and the log object itself.
        """
        path_check, path_log = self.__check_path(tx)
        sqli_check, sqli_log = self.__check_sql_injection(tx)
        
        valid_transaction = path_check or sqli_check
        if isinstance(path_log, SecurityLog): 
            return valid_transaction, path_log
        if isinstance(sqli_log, SecurityLog): 
            return valid_transaction, sqli_log
        else:
            # Not security logs, return path_log for default (for now)
            return valid_transaction, path_log

    
    def contains_block(self, tx: Transaction) -> bool:
        return contains_block(tx)
    
    def __check_path(self, tx: Transaction) -> CheckResult:
        """
        Checks if the resource that the transaction was made for is accessable.
        Accessable = inside the `locations.txt`.
        
        Questions:
        E.g the path: /admin/stats should be blocked?
        """
        path = tx.url.path.decode()
        common = self.locations.intersection({path})
        
        log_object = None
        if common:
            resource = [c for c in common][0]
            file_name = f"{tx.owner.ip}_forbidden_access.log"
            description = f"{tx.owner.ip} made a transaction to access the unauthorized resource {resource}"
            attack_name = "Unauthorized Access"
            log_object = SecurityLog(owner_ip=tx.owner.ip, owner_port=tx.owner.port, file_name=file_name, description=description, attack=attack_name)
            return bool, log_object
        else:
            file_name = f"{tx.owner.ip}_transaction_log.log"
            description = f"Valid transaction."
            creation_date = tx.creation_date
            log_object = AccessLog(owner_ip=tx.owner.ip, owner_port=tx.owner.port, description=description, file_name=file_name, creation_date=creation_date)
            return False, log_object
        
    def __check_sql_injection(self, tx: Transaction) -> CheckResult: 
        """
        Processes the transaction and finds any SQL Injection signatures.
        Can be found at place of the transaction.
        """
        
        # What if an SQL keyword appears at the URI location?
        
        # Check for SQL keywords in the parameters.
        for values in tx.query_params.values():
            for val in values:
                if any(signature in val.decode() for signature in self.sqli):
                    file_name = f"{tx.owner.ip}_sql_injection.log"
                    description = f"SQL Injection attempt while detecting the keyword {val}."
                    attack_name = "SQL Injection"
                    log_object = SecurityLog(owner_ip=tx.owner.ip, owner_port=tx.owner.port, file_name=file_name, description=description, attack=attack_name)
                    return True, log_object
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
        