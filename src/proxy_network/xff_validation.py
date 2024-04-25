# https://adam-p.ca/blog/2022/03/x-forwarded-for - for a great XFF security decisions.

import asyncio
import src.net.aionetwork as anet
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
    valid = anet.convert_netloc(ip) and ip in TRUSTED_PROXY_LIST
    return ip if not valid else None


async def validate_xff_ips(tx: Transaction):
    tx.has_proxies = behind_proxy(tx)
    if not tx.has_proxies:
        tx.real_host_address = tx.owner
        return False, None

    network_layers = [layer.strip() for layer in tx.headers[b"X-Forwarded-For"].decode().split(XFF_SEP)]
    work = [
        anet.create_new_task(
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
            description="Detected a malicious IP address inside an XFF header."
        )
        return True, log

    # ACCESS LOGGING: what about the port?
    # ACCESS LOGGING: Update the real address of the tx.
    if netloc := anet.convert_netloc(network_layers[0]):
        tx.real_host_address = anet.HostAddress(*netloc)
    return False, None
