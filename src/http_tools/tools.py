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

SP = b" "
CR = b"\r"
LF = b"\n"
CRLF = b"\r\n"
BODY_SEPERATOR = b"\r\n\r\n"

# Header seerching ; TODO: Make it perform better.

@dataclass(slots=True)
class Context:
    inner: bytes
    default: Any

class SearchContext:
    HOST = Context(b"Host:", None)
    CONTENT_LENGTH = Context(b"Content-Length:", -1)
    USER_AGENT = Context(b"User-Agent:", None)
    
def contains_body_seperator(request: bytes) -> bool:
    return BODY_SEPERATOR in request

def search_header(request: bytes, context: Context) -> bytes | Any:
    offset = len(context.inner)
    for line in request.split(CRLF):
        if (idx := line.find(context.inner)) >= 0:
            data = line[idx+offset:]
            return data.strip()
    return context.default

def unpack_request_line(request: bytes) -> tuple:
    request_line: bytes = request.split(CRLF)[0]
    method, request_uri, http_version = request_line.strip().split(SP)
    return method, request_uri, http_version