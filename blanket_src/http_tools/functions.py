"""
Author: Daniel Sapojnikov 2023.
http functions module.
"""
from .protocol import HTTPRequestParser

def has_ending_suffix(payload: bytes) -> bool:
    return b'\r\n\r\n' in payload

def get_content_length(payload: HTTPRequestParser, default: int=-1) -> int:
    content_length = payload.getheader('Content-Length', default)
    return int(content_length)

def get_agent(payload: HTTPRequestParser) -> str:
    return payload.getheader('User-Agent', default='Unknown Agent')