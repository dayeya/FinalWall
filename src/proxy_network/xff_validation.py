# https://adam-p.ca/blog/2022/03/x-forwarded-for - for a great XFF security decisions.

import asyncio
from src.net.aionetwork import create_new_task, convert_netloc, HostAddress
from src.internal.system.transaction import Transaction
from src.internal.system.logging import SecurityLog, AttackClassifier

XFF_SEP = ","
TRUSTED_PROXY_LIST = []
TRUSTED_PROXY_COUNT = None


def behind_proxy(tx: Transaction) -> bool:
    if b"X-Forwarded-For" not in tx.headers.keys():
        return False
    return True


async def _validate_ip_address(ip: str):
    valid = convert_netloc(ip) and ip in TRUSTED_PROXY_LIST
    return ip if not valid else None


async def validate_xff_ips(tx: Transaction):
    tx.has_proxies = behind_proxy(tx)
    if not tx.has_proxies:
        tx.real_host_address = tx.owner
        return False, None

    network_layers = [layer.strip() for layer in tx.headers[b"X-Forwarded-For"].decode().split(XFF_SEP)]
    work = [
        create_new_task(
            task_name=f"VALIDATION({ip})",
            task=_validate_ip_address,
            args=(ip,)
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
                "description": "Detected a malicious IP address inside an XFF header",
                "Anonymity": "Yes"
            }
        )
        return True, log

    # ACCESS LOGGING: what about the port?
    if netloc := convert_netloc(network_layers[-1]):
        tx.real_host_address = HostAddress(*netloc)
    return False, None
