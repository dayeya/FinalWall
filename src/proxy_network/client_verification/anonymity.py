import geoip2.database
from pathlib import Path

from src.net.aionetwork import HostAddress
from src.internal.system.transaction import Transaction
from src.proxy_network.client_verification.acl import AccessList

ROOT_DIR = Path(__file__).parent.parent
__mmdb_path = ROOT_DIR / "geoip2_db" / "GeoLite2-Country.mmdb"


def validate_anonymity_from_proxies(tx: Transaction, access_list: AccessList) -> bool:
    """
    Validates the transactions real_host_address by checking if they are anonymous.
    :param tx:
    :param access_list:
    :return:
    """
    pass


def validate_anonymity_from_host(host: HostAddress, access_list: AccessList) -> bool:
    """
    Validates the host by checking if it is an untrusted resource.
    :param host:
    :param access_list:
    :return:
    """
    return host.ip in access_list


def validate_hosts_geoip(host: HostAddress):
    """
    Validates the hosts address of a client.
    :param host:
    :return:
    """
    with geoip2.database.Reader(__mmdb_path) as reader:
        pass


def validate_dirty_client(host: HostAddress, access_list: AccessList) -> bool:
    """
    Validates the clients host address based on its geolocation and anonymity.
    :param host:
    :param access_list:
    :return:
    """
    pass
