"""
Author: Daniel Sapojnikov 2023.
http functions module.
"""
import os
import re
import sys
import base64
from typing import Any, Tuple
from dataclasses import dataclass
from email.parser import BytesParser
from urllib.parse import urlparse, parse_qs, unquote, unquote_to_bytes, ParseResult

HS = b":"
SP = b" "
CR = b"\r"
LF = b"\n"
CRLF = b"\r\n"
BODY_SEPARATOR = b"\r\n\r\n"

PARAM_START = b"?"
PARAM_SEPARATOR = b"&"
PARAM_EQUALS = b"="

# Header searching ; TODO: Make it perform better.


@dataclass(slots=True)
class Context:
    inner: bytes
    default: Any


class SearchContext:
    HOST = Context(b"Host:", None)
    CONTENT_LENGTH = Context(b"Content-Length:", -1)
    USER_AGENT = Context(b"User-Agent:", None)


def contains_body_seperator(request: bytes) -> bool:
    return BODY_SEPARATOR in request


def search_header(request: bytes, context: Context) -> bytes | Any:
    offset = len(context.inner)
    for line in request.split(CRLF):
        if (idx := line.find(context.inner)) >= 0:
            data = line[idx+offset:]
            return data.strip()
    return context.default


def decode_any_encoding(data: bytes) -> str:
    decoded = ""
    try:
        decoded: str = unquote(data)
    except Exception as _url_decoding_err:
        pass
    try:
        decoded: str = str(base64.b64decode(decoded), encoding="utf-8")
    except Exception as _64_decoding_err:
        pass
    return decoded


def process_request_line(request: bytes) -> tuple:
    request_line: bytes = request.split(CRLF, maxsplit=1)[0]
    method, request_uri, http_version = request_line.strip().split(SP)
    request_uri = urlparse(decode_any_encoding(request_uri))
    return method, request_uri, http_version


def process_header(header: bytes) -> tuple:
    if HS in header:
        field_name, field_value = header.split(HS, maxsplit=1)
        return field_name, field_value.rstrip()
    return header, b"not found"


def process_headers_and_body(request: bytes) -> tuple:
    # TODO: Identify multiple value headers.
    message, body = request.split(BODY_SEPARATOR)
    headers: dict = {field: value for field, value in map(process_header, message.split(CRLF)[1:])}
    return headers, decode_any_encoding(body)


def process_query(query: bytes) -> dict:
    """
    Creates a processed dictionary out of a raw byte stream.
    Handles all implemented encoding schemes.
    """
    def _process_query(kv: tuple) -> tuple:
        return decode_any_encoding(kv[0]), map(decode_any_encoding, kv[1])

    params: dict = parse_qs(query, strict_parsing=True)
    decoded_params: dict = dict(map(_process_query, params.items()))
    return decoded_params
