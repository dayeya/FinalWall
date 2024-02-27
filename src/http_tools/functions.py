"""
Author: Daniel Sapojnikov 2023.
http functions module.
"""
import os
import re
import sys
from typing import Tuple, Optional

parent = "../."
module = os.path.abspath(os.path.join(os.path.dirname(__file__), parent))
sys.path.append(module)

from conversion import decode

class SearchContext:
    CONTENT_LENGTH = "Content-Length:" 
    USER_AGENT = "User-Agent:" 
    HOST = "Host:" 
    
CR = "\r"
LF = "\n"
CRLF = "\r\n"
BODY_SEPERATOR = "\r\n\r\n"

def path_segment(payload: str) -> str:
    for header in payload.split('\r\n'):
        match = re.search(r'\b(GET|POST|PUT|DELETE)\s+(/\S*)', header)
        if match:
            return match.groups()

def contains_body_seperator(request: bytes) -> bool:
    return BODY_SEPERATOR in request

def search_header(request: bytes, context: SearchContext) -> bytes:
    try:
        request = decode(request)
        for line in request.split(CRLF):
            if idx := line.find(context) >= 0:
                return line[idx:]
            
    except Exception as e:
        raise e