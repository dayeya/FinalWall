from enum import Enum
from typing import Union
from dataclasses import dataclass


# TODO Make logging as one file or DB.

class AttackClassifier(Enum):
    UNAUTHORIZED_ACCESS = "Unauthorized Access"
    SQL_INJECTION = "SQL Injection"


@dataclass(slots=True)
class LogSettings:
    downloadable: bool


@dataclass(slots=True)
class Log:
    ip: str
    port: int
    creation_date: str


@dataclass(slots=True)
class SecurityLog(Log):
    attack: AttackClassifier
    
    # TODO: how to download the file (Create a download whole alert when hovering on the log).
    # TODO: Data compression.


@dataclass(slots=True)
class AccessLog(Log):
    pass
    
    # TODO: how to download the file (Create a download whole alert when hovering on the log).
    # TODO: Data compression.


type LogType = Union[SecurityLog, AccessLog]