"""
Author: Daniel Sapojnikov 2023.
http functions module.
"""
import os
import re
import sys
from .protocol import *
from typing import Tuple, Optional

parent = "../."
module = os.path.abspath(os.path.join(os.path.dirname(__file__), parent))
sys.path.append(module)

from conversion import decode

type OptionalPathSegment = Tuple[Optional[str]]

def path_segment(payload: str) -> OptionalPathSegment:
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
    try:
        packet: str = decode(packet)
        for header in packet.split('\r\n'):
            idx = header.find('User-Agent')
            if idx >= 0:
                return header[idx:]
    except:
        return None
    
def get_host(packet: bytes) -> str:
    try:
        packet: str = decode(packet)
        for header in packet.split('\r\n'):
            idx = header.find('Host:')
            if idx >= 0:
                return header[idx:]
    except:
        return None
            
__all__ = [
    "path_segment", 
    "has_ending_suffix", 
    "get_content_length", 
    "get_agent",
    "get_host"
]