"""
Author: Daniel Sapojnikov 2023.
http functions module.
"""
import os
import re
import sys
from typing import Any
from dataclasses import dataclass
from email.parser import BytesParser
from urllib.parse import urlparse, parse_qs, ParseResult


parent = "../."
module = os.path.abspath(os.path.join(os.path.dirname(__file__), parent))
sys.path.append(module)

HS = b":"
SP = b" "
CR = b"\r"
LF = b"\n"
CRLF = b"\r\n"
BODY_SEPERATOR = b"\r\n\r\n"

PARAM_START = b"?"
PARAM_SEPARATOR = b"&"
PARAM_EQUALS = b"="

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

def process_request_line(request: bytes) -> tuple:
    request_line: bytes = request.split(CRLF, maxsplit=1)[0]
    method, request_uri, http_version = request_line.strip().split(SP)
    request_uri = urlparse(request_uri)
    return method, request_uri, http_version

def process_header(header: bytes) -> tuple:
    if HS in header:
        field_name, field_value = header.split(HS, maxsplit=1)
        return field_name, field_value.rstrip()
    return header, b"Not valid"

def process_headers_and_body(request: bytes) -> tuple: 
    # TODO: Identify multiple value headers.
    message, body = request.split(BODY_SEPERATOR)
    headers: dict = {field: value for field, value in map(process_header, message.split(CRLF)[1:])}
    return headers, body

def process_query(query: bytes) -> dict:
    params: dict = parse_qs(query, strict_parsing=True)
    return params