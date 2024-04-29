import asyncio

from src.internal.system.check_types import CheckResult
from src.internal.system.transaction import Transaction
from src.internal.system.logging import SecurityLog, AttackClassifier
from src.net.aionetwork import create_new_task, convert_netloc, HostAddress

from src.proxy_network.client_verification.acl import AccessList
from src.proxy_network.client_verification.anonymity import validate_dirty_client

XFF_SEP = ","


def behind_proxy(tx: Transaction) -> bool:
    return b"X-Forwarded-For" in tx.headers.keys()


async def __validate_ip_address(ip: str, access_list: AccessList, banned_countries: list) -> str | None:
    valid_netloc = convert_netloc(ip)
    dirty_client = validate_dirty_client(ip, access_list, banned_countries)
    passed = valid_netloc and dirty_client == 0
    if passed:
        return None
    return ip


async def validate_xff_ips(tx: Transaction, access_list: AccessList, banned_countries) -> CheckResult:
    tx.has_proxies = behind_proxy(tx)
    if not tx.has_proxies:
        tx.real_host_address = tx.owner
        return CheckResult(result=False, log=None)

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
        log = SecurityLog(
            attack=AttackClassifier.IP_SPOOFING,
            ip=tx.owner.ip,
            port=tx.owner.port,
            creation_date=tx.creation_date,
            malicious_data=", ".join(blacklisted_proxies).encode("utf-8"),
            metadata={
                "Description": "Detected a malicious IP address inside an XFF header",
                "Anonymity": "Yes"
            }
        )
        return CheckResult(result=True, log=log)

    # check if the trusted address from the xff.
    if netloc := convert_netloc(network_layers[-1]):
        tx.real_host_address = HostAddress(*netloc)

    return CheckResult(result=False, log=None)
