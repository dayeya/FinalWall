"""
Author: Daniel Sapojnikov 2023.
http functions module.
"""
import re
from typing import Tuple, Optional
from .protocol import HTTPResponseParser

def path_segment(payload: str) -> Tuple[Optional[str]]:
    for header in payload.split('\r\n'):
        match = re.search(r'\b(GET|POST|PUT|DELETE)\s+(/\S*)', header)
        if match:
            return match.groups()

def has_ending_suffix(packet: bytes) -> bool:
    return b'\r\n\r\n' in packet

def get_content_length(packet: bytes, default: int=-1) -> int:
    packet = HTTPResponseParser(packet)
    content_length = packet.getheader('Content-Length', default)
    return int(content_length)

def get_agent(packet: bytes) -> str:
    packet = HTTPResponseParser(packet)
    return packet.getheader('User-Agent', default='Unknown Agent')

__all__ = ["path_segment", "has_ending_suffix", "get_content_length", "get_agent"]