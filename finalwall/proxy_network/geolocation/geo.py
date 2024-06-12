#
# FinalWall - A GeoIP API for geo-information gathering.
# Author: Dayeya.
# Credit: MaxMind.
#

import json
import requests
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
    city: str

    def __repr__(self) -> str:
        return f"{self.continent}, {self.country} - {self.city}"


def get_external_ip() -> str:
    """Uses the API of ipify.org to fetch the external IP of the cluster."""
    response = requests.get("https://api.ipify.org?format=json").text
    return json.loads(response)["ip"]


def get_geoip_data(ip: str) -> GeoData | None:
    """Gets the geoip data regarding an ip address."""
    try:
        with geoip2.database.Reader(__mmdb_path) as reader:
            response = reader.city(ip)
            return GeoData(
                continent=response.continent.name,
                country=response.country.name,
                city=response.city.name,
            )
    except geoip2.errors.AddressNotFoundError:
        return None


def validate_geoip_data(ip: str, banned_countries: list) -> bool:
    geodata = get_geoip_data(ip)
    if geodata is None:
        # client is not found on the db, assuming he is not valid.
        return False
    return geodata.country in banned_countries
