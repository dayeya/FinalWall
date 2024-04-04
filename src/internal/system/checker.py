from typing import Tuple
from src.components.singleton import Singleton
from src.internal.database import SignaturesDB
from src.internal.system.transaction import Transaction
from src.internal.system.actions.block import contains_block
from src.internal.system.logging import AttackClassifier, SecurityLog, AccessLog, LogType


# CheckResult = [Malicious or not, A log object]
type CheckResult = Tuple[bool, LogType]


class Checker(metaclass=Singleton):
    def check_transaction(self, tx: Transaction) -> CheckResult:
        """
        Checks `tx` for each attack and creates a log object (Can be either access or security).
        :returns: CheckResult holding if the transaction is malicious or not, and the log object itself.
        """
        unauthorized, log = self.__check_path(tx)
        if unauthorized:
            return unauthorized, log
        sqli, log = self.__check_sql_injection(tx)
        if sqli:
            return sqli, log
        
        log = AccessLog(ip=tx.owner.ip, port=tx.owner.port, creation_date=tx.creation_date)
        return False, log

    @staticmethod
    def contains_block(tx: Transaction) -> bool:
        return contains_block(tx)

    @staticmethod
    def __check_path(tx: Transaction) -> CheckResult:
        """
        Checks if the resource that the transaction was made for is authorized.
        """
        log = None
        db: SignaturesDB = SignaturesDB()
        unauthorized_access: bool = any({loc in tx.url.path for loc in db.unauthorized_access_data_set})

        if unauthorized_access:
            log = SecurityLog(attack=AttackClassifier.UNAUTHORIZED_ACCESS, ip=tx.owner.ip, port=tx.owner.port, creation_date=tx.creation_date)
            return True, log
        return False, None

    @staticmethod
    def __check_sql_injection(tx: Transaction) -> CheckResult:
        """
        Processes the transaction and finds any SQL injection signatures.
        """
        db: SignaturesDB = SignaturesDB()
        for values in tx.query_params.values():
            for val in values:
                if any([signature in val for signature in db.sql_data_set]):
                    log = SecurityLog(attack=AttackClassifier.SQL_INJECTION, ip=tx.owner.ip, port=tx.owner.port, creation_date=tx.creation_date)
                    return True, log
        return False, None

    @staticmethod
    def __check_context(substring: str) -> CheckResult:
        # if `'` is present than the query might exit the context.
        # To ensure query validation the query MUST return the context without injecting SQL payloads.
        # To check it we need to check for context escaping and if sql payload checks.
        # The payload `'; DELETE users` will delete the table.
        # O'Brian
        pass

    @staticmethod
    def __check_xss(self, tx) -> None:
        pass
        