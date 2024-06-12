#
# FinalWall - Anonymity validation.
# Author: Dayeya
#

from .acl import AccessList


def validate_anonymity_from_ip(ip: str, access_list: AccessList) -> bool:
    """Validates an IP address by checking if it is blacklisted."""
    return ip in access_list
