#
# FinalWall - functions that check vulnerabilities on transactions.
# Author: Dayeya
#

import asyncio
from typing import Callable

from ..events import Classifier
from ._types import Check, CheckResult
from ._types import SQL_INJECTION, XSS, LFI, RFI, BRUTEFORCE, UNAUTHORIZED_ACCESS, ANONYMOUS, GEOLOCATION

from ..core.transaction import Transaction
from ..signature_db import SignatureDb

from finalwall.http_process import Header
from finalwall.net import create_new_task, convert_netloc, HostAddress
from finalwall.proxy_network.geolocation import validate_geoip_data
from finalwall.proxy_network.anonymity import AccessList, validate_anonymity_from_ip

XFF_SEP = ","
PAIR_SEPARATOR = ","


def __encapsulated(a, b) -> bool:
    """
    Checks for encapsulation state of `a` and `b`.
    This function is called when checking if a signature is inside a value or otherwise.
    """
    return a in b or b in a


def __case_sensitive(condition: Callable, *args) -> bool:
    """
    Wrapper function that executes `condition` on *args in its str.lower() and str.upper() form.
    This handles cases where input is in lower and upper form.
    """
    if any(not isinstance(arg, str) for arg in args):
        print("Bad arguments for __case_sensitive!")
    upper, lower = [arg.upper() for arg in args], [arg.lower() for arg in args]
    return condition(*upper) or condition(*lower)


async def __validate_ip_address(ip: str, access_list: AccessList, banned_countries: list) -> tuple[str, int] | None:
    """
    Validates a single ip address.
    :param ip:
    :param access_list:
    :param banned_countries:
    :return:
    """
    valid_netloc = convert_netloc(ip)
    dirty_client = validate_dirty_client(ip, access_list, banned_countries)
    passed = valid_netloc and dirty_client == 0
    if passed:
        return None
    return ip, dirty_client


def classify_by_flags(flags: int) -> list[Classifier]:
    """
    Classify flags to their corresponding classifiers.
    :param flags:
    :return:
    """
    classifiers = []
    if flags & SQL_INJECTION:
        classifiers.append(Classifier.SqlInjection)
    if flags & XSS:
        classifiers.append(Classifier.XSS)
    if flags & LFI:
        classifiers.append(Classifier.LFI)
    if flags & RFI:
        classifiers.append(Classifier.RFI)
    if flags & BRUTEFORCE:
        classifiers.append(BRUTEFORCE)
    if flags & UNAUTHORIZED_ACCESS:
        classifiers.append(Classifier.UnauthorizedAccess)
    if flags & ANONYMOUS:
        classifiers.append(Classifier.Anonymity)
    if flags & GEOLOCATION:
        classifiers.append(Classifier.BannedGeolocation)
    return classifiers


async def validate_xff(tx: Transaction, access_list: AccessList, banned_countries) -> CheckResult:
    """
    Validates the xff header (if any) of a transaction.
    :param tx:
    :param access_list:
    :param banned_countries:
    :return:
    """
    if not Header.XFF.inside(tx.headers.keys()):
        tx.real_host_address = tx.owner
        return CheckResult(result=False, classifiers=[])

    layers = tx.headers["X-Forwarded-For"].split(XFF_SEP)
    network_layers = [layer.strip() for layer in layers]
    work = [
        create_new_task(
            task_name=f"VALIDATION({ip})",
            task=__validate_ip_address,
            args=(ip, access_list, banned_countries)
        ) for ip in network_layers
    ]
    results = await asyncio.gather(*work)
    blacklisted_proxies = list(filter(lambda tup: tup[0] is not None, results))

    print(blacklisted_proxies)
    print(classify_by_flags(blacklisted_proxies[0][1]))

    if blacklisted_proxies:
        return CheckResult(result=True, classifiers=classify_by_flags(blacklisted_proxies[0][1]))

    # check if the trusted address from the xff.
    tx.real_host_address = HostAddress(ip=network_layers[-1], port=tx.owner.port)
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


async def check_path(tx: Transaction) -> CheckResult:
    """
    Validates the transactions request URI namely `tx.url.path` by checking if it`s a banned resource or not.
    :param tx:
    :return:
    """
    async with asyncio.Lock():
        db: SignatureDb = SignatureDb()
        unauthorized_access = any({loc in tx.url.path for loc in db.unauthorized_access_data_set})
        if not unauthorized_access:
            return CheckResult(result=False, classifiers=[])
        return CheckResult(result=True, classifiers=[Classifier.UnauthorizedAccess])


async def check_sql_injection(tx: Transaction) -> CheckResult:
    """
    Validates some areas of the transaction that potentially carry SQLi signatures.
    Checks for lone SQLi signatures and for paired ones.
    """
    def _check_keyword_in_pairs(param: str, _pairs: list) -> bool:
        """
        Simple helper function called when checking for pairs of SQLi signatures.

        Suppose we have the following URI:

            http:<ip>:<port>/register?=username=`UNION SELECT * FROM))`

        Here, `SELECT` is paired with `UNION`, `*` and `FROM`.
        """
        single_pairs: set = set(filter(lambda p: PAIR_SEPARATOR not in p, _pairs))
        multiple_pairs: set = set(filter(lambda p: PAIR_SEPARATOR in p, _pairs))
        if any(p in param for p in single_pairs):
            return True
        if any({all(sub_pair in param for sub_pair in p.split(PAIR_SEPARATOR)) for p in multiple_pairs}):
            return True
        return False

    # Check for context escaping chars.
    for values in tx.query_params.values():
        for value in values:
            if value.startswith("`"):
                return CheckResult(result=True, classifiers=[Classifier.SqlInjection])

    # Signature checking.
    async with asyncio.Lock():
        db: SignatureDb = SignatureDb()
        for values in tx.query_params.values():
            for current_query_val in values:
                if any(__case_sensitive(lambda a, b: a in b, sig, current_query_val) for sig in db.sql_data_set["general_keywords"]):
                    return CheckResult(result=True, classifiers=[Classifier.SqlInjection])

                for keyword, pairs in db.sql_data_set["keywords_with_pairs"].items():
                    if __case_sensitive(lambda a, b: a in b, keyword, current_query_val) and _check_keyword_in_pairs(current_query_val, pairs):
                        return CheckResult(result=True, classifiers=[Classifier.SqlInjection])
        return CheckResult(result=False, classifiers=[])


async def check_xss(tx: Transaction) -> CheckResult:
    """
    Validates some areas of the transaction that potentially carry XSS signatures.
    """
    async with asyncio.Lock():
        db: SignatureDb = SignatureDb()
        for values in tx.query_params.values():
            for current_query_val in values:
                if any(signature in current_query_val for signature in db.xss_data_set["keywords"]):
                    return CheckResult(result=True, classifiers=[Classifier.XSS])
        return CheckResult(result=False, classifiers=[])


async def check_transaction(tx: Transaction, access_list: AccessList, banned_countries: list) -> CheckResult:
    """
    Analyzes a transaction for several vulnerabilities by performing checks.
    :returns: CheckResult
    """
    checks = [
        Check(fn=validate_xff, args=(tx, access_list, banned_countries)),
        Check(fn=check_path, args=(tx,)),
        Check(fn=check_sql_injection, args=(tx,)),
        Check(fn=check_xss, args=(tx,))
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
