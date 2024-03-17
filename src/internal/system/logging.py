from dataclasses import dataclass
from typing import Union

@dataclass(slots=True)
class SecurityLog:
    owner_ip: str
    owner_port: int
    file_name: str 
    description: str
    attack: str
    
    # TODO: how to download the file (Create a download whole alert when hovering on the log).
    # TODO: Data compression.


@dataclass(slots=True)
class AccessLog:
    owner_ip: str
    owner_port: int
    description: str
    file_name: str
    creation_date: str
    
    # TODO: how to download the file (Create a download whole alert when hovering on the log).
    # TODO: Data compression.
    
type LogType = Union[SecurityLog, AccessLog]


# Make logging as one file or DB.