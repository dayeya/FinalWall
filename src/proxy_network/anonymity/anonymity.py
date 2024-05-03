from src.proxy_network.anonymity.acl import AccessList


def validate_anonymity_from_ip(ip: str, access_list: AccessList) -> bool:
    """
    Validates the ip by checking if it is an untrusted ip.
    :param ip:
    :param access_list:
    :return:
    """
    return ip in access_list
