from typing import Union
from dataclasses import dataclass
from urllib.parse import unquote, parse_qs

@dataclass
class SqlDetectionResult:
    result: bool
    description: str

@dataclass
class SqlPayload:
    payload: str
    identifier: str
        
    def len(self) -> int:
        return len(self.payload)
    
def decode_url(raw: str) -> str:
    return unquote(raw)
    
def with_quotes(s: SqlPayload) -> bool:
    pass

def with_keywords(s: SqlPayload) -> bool:
    pass

def sqli(s: SqlPayload) -> SqlDetectionResult: 
    if s.len() == 0:
        return SqlDetectionResult(True, 'Empty payload')
    