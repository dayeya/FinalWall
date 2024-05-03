import asyncio

from .types import Check, ANONYMOUS, GEOLOCATION
from src.internal.database import SignatureDb
from src.internal.system.types import CheckResult
from src.internal.system.transaction import Transaction
from src.internal.system.logging import AttackClassifier
from src.http_process.headers import Header
from src.net.aionetwork import create_new_task, convert_netloc, HostAddress
from src.proxy_network.geolocation import validate_geoip_data
from src.proxy_network.anonymity import AccessList, validate_anonymity_from_ip

XFF_SEP = ","
PAIR_SEPARATOR = ","


def classify_by_flags(flags: int) -> list[AttackClassifier]:
    """
    Classify the flags of a dirty_client_validation.
    :param flags:
    :return:
    """
    classifiers = []
    if flags & ANONYMOUS:
        classifiers.append(AttackClassifier.Anonymity)
    if flags & GEOLOCATION:
        classifiers.append(AttackClassifier.Banned_Geolocation)
    return classifiers


async def __validate_ip_address(ip: str, access_list: AccessList, banned_countries: list) -> str | None:
    valid_netloc = convert_netloc(ip)
    dirty_client = validate_dirty_client(ip, access_list, banned_countries)
    passed = valid_netloc and dirty_client == 0
    if passed:
        return None
    return ip


async def _validate_xff(tx: Transaction, access_list: AccessList, banned_countries) -> CheckResult:
    """
    Validates the xff header (if any) of a transaction.
    :param tx:
    :param access_list:
    :param banned_countries:
    :return:
    """
    if Header.XFF not in tx.headers.keys() or Header.PROXY_CONNECTION not in tx.headers.keys():
        tx.real_host_address = tx.owner
        return CheckResult(result=False, classifiers=[])

    layers = tx.headers[b"X-Forwarded-For"].decode().split(XFF_SEP)
    network_layers = [layer.strip() for layer in layers]
    work = [
        create_new_task(
            task_name=f"VALIDATION({ip})",
            task=__validate_ip_address,
            args=(ip, access_list, banned_countries)
        ) for ip in network_layers
    ]
    results = await asyncio.gather(*work)
    blacklisted_proxies = list(filter(None, results))

    if blacklisted_proxies:
        return CheckResult(result=True, classifiers=[])

    # check if the trusted address from the xff.
    if netloc := convert_netloc(network_layers[-1]):
        tx.real_host_address = HostAddress(*netloc)

    return CheckResult(result=False, classifiers=[])


def validate_dirty_client(ip: str, access_list: AccessList, banned_countries: list) -> int:
    """
    Validates the clients host address based on its geolocation and anonymity.
    :param banned_countries:
    :param ip:
    :param access_list:
    :return:
    """
    anonymous = validate_anonymity_from_ip(ip, access_list)
    geolocation = validate_geoip_data(ip, banned_countries)
    result = ANONYMOUS if anonymous else 0 | GEOLOCATION if geolocation else 0
    return result


async def _check_path(tx: Transaction) -> CheckResult:
    async with asyncio.Lock():
        db: SignatureDb = SignatureDb()
        unauthorized_access = any({loc in tx.url.path for loc in db.unauthorized_access_data_set})
        if not unauthorized_access:
            return CheckResult(result=False, classifiers=[])
        return CheckResult(result=True, classifiers=[AttackClassifier.Unauthorized_access])


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
                    return CheckResult(result=True, classifiers=[AttackClassifier.Sql_Injection])

                for keyword, pairs in db.sql_data_set["keywords_with_pairs"].items():
                    if keyword in current_query_val and _check_keyword_in_pairs(current_query_val, pairs):
                        return CheckResult(result=True, classifiers=[AttackClassifier.Sql_Injection])
        return CheckResult(result=False, classifiers=[])


async def check_transaction(tx: Transaction, access_list: AccessList, banned_countries: list) -> CheckResult:
    """
    Analyzes a transaction for several vulnerabilities.
    :returns: CheckResult
    """
    checks = [
        Check(fn=_validate_xff, args=(tx, access_list, banned_countries)),
        Check(fn=_check_path, args=(tx,)),
        Check(fn=_check_sql_injection, args=(tx,))
    ]

    work = [create_new_task(task=check.fn, args=check.args) for check in checks]
    results: tuple[CheckResult] = await asyncio.gather(*work)
    for result in results:
        if result.result:
            return result

    # None of the checks have passed, transaction is valid.
    return CheckResult(result=False, classifiers=[])


__all__ = [
    "check_transaction",
    "validate_dirty_client",
    "classify_by_flags"
]
