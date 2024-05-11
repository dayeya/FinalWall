import geoip2.database
import geoip2.errors
from pathlib import Path
from dataclasses import dataclass

ROOT_DIR = Path(__file__).parent
__mmdb_path = ROOT_DIR / "geoip2_db" / "GeoLite2-City.mmdb"


@dataclass(slots=True)
class GeoData:
    continent: str
    country: str
    country_confidence: int
    city: str
    city_confidence: int


def get_geoip_data(ip: str) -> GeoData | None:
    """
    Gets the geoip data regarding an ip address.
    :param ip:
    :return:
    """
    try:
        with geoip2.database.Reader(__mmdb_path) as reader:
            response = reader.city(ip)
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
