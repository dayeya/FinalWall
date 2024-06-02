"""
Author: Daniel Sapojnikov 2023.
http functions module.
"""
import base64
from dataclasses import dataclass
from email.parser import BytesParser
from typing import Any, Iterable, Union
from urllib.parse import urlparse, parse_qs, unquote, unquote_to_bytes, ParseResult

HS = b":"
SP = b" "
CR = b"\r"
LF = b"\n"
CRLF = b"\r\n"
BODY_SEPARATOR = b"\r\n\r\n"
IP_OCTET_SEPARATOR = "."
PORT_SEPERATOR = ":"


@dataclass(slots=True)
class Context:
    name: bytes
    default: Any


class SearchContext:
    HOST = Context(b"Host:", None)
    CONTENT_LENGTH = Context(b"Content-Length:", -1)
    USER_AGENT = Context(b"User-Agent:", None)


def contains_body_seperator(request: bytes) -> bool:
    return BODY_SEPARATOR in request


def search_header(request: bytes, context: Context) -> bytes | Any:
    offset = len(context.name)
    for line in request.split(CRLF):
        if (idx := line.find(context.name)) >= 0:
            data = line[idx + offset:]
            return data.strip()
    return context.default


def decode_any_encoding(data: Union[bytes, Iterable[bytes]]) -> Union[str, Iterable[str]]:
    def _decode_datagram(datagram: bytes) -> str:
        decoded = ""
        try:
            decoded: str = unquote(datagram)
        except Exception as _url_decoding_err:
            pass
        try:
            decoded: str = str(base64.b64decode(decoded), encoding="utf-8")
        except Exception as _64_decoding_err:
            pass
        return decoded

    if isinstance(data, str):
        return data
    if isinstance(data, bytes):
        return _decode_datagram(data)
    return [_decode_datagram(datagram) for datagram in data]


def process_request_line(request: bytes) -> tuple:
    request_line: bytes = request.split(CRLF, maxsplit=1)[0]
    method, request_uri, http_version = request_line.strip().split(SP)
    request_uri = urlparse(decode_any_encoding(request_uri))
    return method, request_uri, http_version


def process_header(header: bytes) -> tuple:
    field_name, sep, field_value = header.rpartition(HS)
    assert sep  # b":" Must be present.
    return field_name.decode(), field_value.strip().decode()


def process_headers_and_body(request: bytes) -> tuple:
    try:
        message, body = request.split(BODY_SEPARATOR)
        headers: dict = {field: value for field, value in map(process_header, message.split(CRLF)[1:])}
        return headers, decode_any_encoding(body)
    except ValueError:
        """No body."""
        return {}, ""


def process_query(query: bytes) -> dict:
    """
    Creates a processed dictionary out of raw.
    Handles all implemented encoding schemes.
    """
    def _decode_query(field: bytes, values: Iterable[bytes]) -> tuple[str, Iterable[str]]:
        return decode_any_encoding(field), list(map(decode_any_encoding, values))

    params: dict = parse_qs(query, strict_parsing=True)
    decoded_params: dict = dict(map(lambda item: _decode_query(*item), params.items()))
    return decoded_params


def decode_headers(headers: dict) -> dict:
    """Decodes the headers and their values if needed."""
    try:
        return {header.decode("utf-8"): value.decode("utf-8") for header, value in headers.items()}
    except AttributeError:
        return headers
