import asyncio

from .check_types import Check, CheckResult
from src.net.aionetwork import create_new_task

from src.internal.database import SignatureDb
from src.internal.system.transaction import Transaction
from src.internal.system.logging import AttackClassifier, SecurityLog, AccessLog

from src.proxy_network.client_verification.acl import AccessList
from src.proxy_network.client_verification.anonymity import get_geoip_data
from src.proxy_network.client_verification.xff_validation import validate_xff_ips


PAIR_SEPARATOR = ","


async def _check_path(tx: Transaction) -> CheckResult:
    async with asyncio.Lock():
        db: SignatureDb = SignatureDb()
        unauthorized_access = any({loc in tx.url.path for loc in db.unauthorized_access_data_set})

        if not unauthorized_access:
            return CheckResult(result=False, log=None)

        # Malicious attempt to access an unauthorized resource.
        log = SecurityLog(
            attack=AttackClassifier.UNAUTHORIZED_ACCESS,
            ip=tx.owner.ip,
            port=tx.owner.port,
            creation_date=tx.creation_date,
            malicious_data=tx.url.path,
            metadata={"Geodata": get_geoip_data(tx.owner.ip)}
        )
        return CheckResult(result=True, log=log)


async def _check_sql_injection(tx: Transaction) -> CheckResult:
    def _check_keyword_in_pairs(value: str, _pairs: list) -> bool:
        single_pairs: set = set(filter(lambda p: PAIR_SEPARATOR not in p, _pairs))
        multiple_pairs: set = set(filter(lambda p: PAIR_SEPARATOR in p, _pairs))
        if any(p in value for p in single_pairs):
            return True
        if any({all(sub_pair in value for sub_pair in p.split(PAIR_SEPARATOR)) for p in multiple_pairs}):
            return True
        return False

    async with asyncio.Lock():
        db: SignatureDb = SignatureDb()
        for values in tx.query_params.values():
            for current_query_val in values:
                if any(signature in current_query_val for signature in db.sql_data_set["general_keywords"]):
                    log = SecurityLog(
                        attack=AttackClassifier.SQL_INJECTION,
                        ip=tx.owner.ip,
                        port=tx.owner.port,
                        creation_date=tx.creation_date,
                        malicious_data=current_query_val,
                        metadata={"Geodata": get_geoip_data(tx.real_host_address.ip)}
                    )
                    return CheckResult(result=True, log=log)

                for keyword, pairs in db.sql_data_set["keywords_with_pairs"].items():
                    if keyword in current_query_val and _check_keyword_in_pairs(current_query_val, pairs):
                        log = SecurityLog(
                            attack=AttackClassifier.SQL_INJECTION,
                            ip=tx.owner.ip,
                            port=tx.owner.port,
                            creation_date=tx.creation_date,
                            malicious_data=current_query_val,
                            metadata={"Geodata": get_geoip_data(tx.real_host_address.ip)}
                        )
                        return CheckResult(result=True, log=log)
        return CheckResult(result=False, log=None)


async def check_transaction(tx: Transaction, access_list: AccessList, banned_countries: list) -> CheckResult:
    """
    Analyzes a transaction for several vulnerabilities.
    :returns: CheckResult
    """
    checks = [
        Check(fn=validate_xff_ips, args=(tx, access_list, banned_countries)),
        Check(fn=_check_path, args=(tx,)),
        Check(fn=_check_sql_injection, args=(tx,))
    ]

    work = [create_new_task(task=check.fn, args=check.args) for check in checks]
    results: tuple[CheckResult] = await asyncio.gather(*work)
    for result in results:
        if result.unwrap():
            return result

    # None of the checks have passed, transaction is valid.
    log = AccessLog(
        ip=tx.real_host_address.ip if tx.real_host_address is not None else tx.owner.port,
        port=tx.real_host_address.port if tx.real_host_address is not None else tx.owner.port,
        creation_date=tx.creation_date
    )
    return CheckResult(result=False, log=log)


__all__ = [
    "check_transaction"
]
