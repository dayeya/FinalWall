from pathlib import Path
from functools import lru_cache
from dataclasses import dataclass
import geoip2.database, geoip2.errors

from src.proxy_network.client_verification.acl import AccessList

ROOT_DIR = Path(__file__).parent.parent
__mmdb_path = ROOT_DIR / "geoip2_db" / "GeoLite2-City.mmdb"


class VerificationFlag:
    ANONYMOUS = 1
    GEOLOCATION = 2


@dataclass(slots=True)
class GeoData:
    continent: str
    country: str
    country_confidence: int
    city: str
    city_confidence: int


def validate_anonymity_from_ip(ip: str, access_list: AccessList) -> bool:
    """
    Validates the ip by checking if it is an untrusted ip.
    :param ip:
    :param access_list:
    :return:
    """
    return ip in access_list


def get_geoip_data(ip: str) -> GeoData | None:
    """
    Gets the geoip data regarding an ip address.
    :param ip:
    :return:
    """
    try:
        with geoip2.database.Reader(__mmdb_path) as reader:
            response = reader.city(ip)
            print(response)
            return GeoData(
                continent=response.continent.name,
                country=response.country.iso_code,
                country_confidence=response.country.confidence,
                city=response.city.name,
                city_confidence=response.city.confidence,
            )
    except geoip2.errors.AddressNotFoundError:
        return None


def validate_geoip_data(ip: str, banned_countries: list) -> bool:
    geodata = get_geoip_data(ip)
    if geodata is None:
        # client is not found on the db, assuming he is not valid.
        return False
    return geodata.country in banned_countries


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
    result = VerificationFlag.ANONYMOUS if anonymous else 0 | VerificationFlag.GEOLOCATION if geolocation else 0
    return result
