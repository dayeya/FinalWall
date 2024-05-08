from dataclasses import dataclass
from typing import Union, Optional

from .classifier import Classifier
from src.proxy_network.geolocation import GeoData


@dataclass(slots=True)
class Log:
    """
    A basic class holding the basic fields that either a Security Log and an Access Log hold.
    """
    ip: str
    port: int
    download: bool
    creation_date: str


@dataclass(slots=True)
class SecurityLog(Log):
    """
    A log object that is created when a Waf instance detected a potential attack or threat.
    """
    classifiers: list[Classifier]
    geolocation: GeoData
    malicious_data: Optional[bytes] = None
    metadata: Optional[dict] = None


@dataclass(slots=True)
class AccessLog(Log):
    """
    A log object representing valid client transactions.
    """
    pass


type LogObject = Union[SecurityLog, AccessLog]
