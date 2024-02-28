"""
Author: Daniel Sapojnikov 2023.
http functions module.
"""
import os
import re
import sys
from typing import Any
from dataclasses import dataclass

parent = "../."
module = os.path.abspath(os.path.join(os.path.dirname(__file__), parent))
sys.path.append(module)

    
CR = b"\r"
LF = b"\n"
CRLF = b"\r\n"
BODY_SEPERATOR = b"\r\n\r\n"

@dataclass(slots=True)
class Context:
    inner: bytes
    default: Any

class SearchContext:
    HOST = Context(b"Host:", "Unknown")
    CONTENT_LENGTH = Context(b"Content-Length:", -1)
    USER_AGENT = Context(b"User-Agent:", "Unknown")

# TODO: make this function more efficient.
def path_segment(payload: str) -> str:
    for header in payload.split('\r\n'):
        match = re.search(r'\b(GET|POST|PUT|DELETE)\s+(/\S*)', header)
        if match:
            return match.groups()

def contains_body_seperator(request: bytes) -> bool:
    return BODY_SEPERATOR in request

def search_header(request: bytes, context: Context) -> bytes:
    offset = len(context.inner)
    for line in request.split(CRLF):
        if (idx := line.find(context.inner)) >= 0:
            data = line[idx+offset:]
            return data.strip()
    return context.default