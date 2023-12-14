"""
Author: Daniel Sapojnikov 2023.
http functions module.
"""
from .protocol import HTTPRequestParser

END_SUFFIX = b'\r\n\r\n'
    
def has_ending_suffix(payload: bytes) -> bool:
    return END_SUFFIX in payload

def get_content_length(payload: HTTPRequestParser, default: int=-1) -> int:
    content_length = payload.getheader('Content-Length', default)
    return int(content_length)