import asyncio
from typing import Tuple
from src.internal.database import SignaturesDB
from src.internal.system.transaction import Transaction
from src.internal.system.actions.block import contains_block
from src.proxy_network.xff_validation import validate_xff_ips
from src.internal.system.logging import AttackClassifier, SecurityLog, AccessLog, LogType


# CheckResult = [Malicious or not, A log object]
type CheckResult = Tuple[bool, LogType | None]

PAIR_SEPARATOR = ","


class Checker:
    async def check_transaction(self, tx: Transaction) -> CheckResult:
        """
        Checks `tx` for each attack and creates a log object (Can be either access or security).
        :returns: CheckResult holding if the transaction is malicious or not, and the log object itself.
        """
        xff, log = await validate_xff_ips(tx)
        if xff:
            return xff, log
        unauthorized, log = await self.__check_path(tx)
        if unauthorized:
            return unauthorized, log
        sqli, log = await self.__check_sql_injection(tx)
        if sqli:
            return sqli, log

        log = AccessLog(
            ip=tx.real_host_address.ip if tx.real_host_address is not None else tx.owner.port,
            port=tx.real_host_address.port if tx.real_host_address is not None else tx.owner.port,
            creation_date=tx.creation_date,
        )
        return False, log

    @staticmethod
    def contains_block(tx: Transaction) -> str | None:
        return contains_block(tx)

    @staticmethod
    async def __check_path(tx: Transaction) -> CheckResult:
        """
        Checks if the resource that the transaction was made for is authorized.
        """
        async with asyncio.Lock():
            db: SignaturesDB = SignaturesDB()
            unauthorized_access = any({loc in tx.url.path for loc in db.unauthorized_access_data_set})
            if unauthorized_access:
                log = SecurityLog(
                    attack=AttackClassifier.UNAUTHORIZED_ACCESS,
                    ip=tx.owner.ip,
                    port=tx.owner.port,
                    creation_date=tx.creation_date,
                    malicious_data=tx.url.path,
                    metadata={}
                )
                return True, log
            return False, None

    @staticmethod
    async def __check_sql_injection(tx: Transaction) -> CheckResult:
        """
        Processes the transaction and finds any SQL injection signatures.
        """
        def _check_keyword_in_pairs(value: str, _pairs: list) -> bool:
            single_pairs: set = set()
            multiple_pairs: set = set()
            for pair_signature in _pairs:
                if PAIR_SEPARATOR in pair_signature:
                    multiple_pairs.add(pair_signature)
                else:
                    single_pairs.add(pair_signature)
            if any(p in value for p in single_pairs):
                return True
            if any({all(sub_pair in value for sub_pair in p.split(PAIR_SEPARATOR)) for p in multiple_pairs}):
                return True
            return False

        async with asyncio.Lock():
            db: SignaturesDB = SignaturesDB()
            for values in tx.query_params.values():
                for current_query_val in values:
                    if any(signature in current_query_val for signature in db.sql_data_set["general_keywords"]):
                        log = SecurityLog(
                            attack=AttackClassifier.SQL_INJECTION,
                            ip=tx.owner.ip,
                            port=tx.owner.port,
                            creation_date=tx.creation_date,
                            malicious_data=current_query_val,
                            metadata={}
                        )
                        return True, log

                    for keyword, pairs in db.sql_data_set["keywords_with_pairs"].items():
                        if keyword in current_query_val and _check_keyword_in_pairs(current_query_val, pairs):
                            log = SecurityLog(
                                attack=AttackClassifier.SQL_INJECTION,
                                ip=tx.owner.ip,
                                port=tx.owner.port,
                                creation_date=tx.creation_date,
                                malicious_data=current_query_val,
                                metadata={}
                            )
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
        