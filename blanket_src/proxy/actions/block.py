#Simple file that defines the behavior of a BLOCK.

import re
from pathlib import Path
from jinja2 import Environment
from conversion import encode, decode

BASE_FILE = __file__
HTML_FILE = "security_page.html"
BLOCK_REGEX = re.compile(r"GET /block[?]token=([a-z0-9]{8})")
ENV = Environment()

def abs_component_path(location: str) -> str:
    parent = Path(BASE_FILE).parent.joinpath('security_page')
    location = str(parent.joinpath(location))
    return location

def push_args_into_template(*args, **kwargs) -> bytes:
    html_file = abs_component_path(HTML_FILE)
    with open(html_file, 'r') as h:
        html = h.read()
    block_template = ENV.from_string(html)
    return encode(block_template.render(*args, **kwargs))

def build_redirect(location: bytes) -> bytes:
    redirect = b"HTTP/1.1 302 Found\r\n"
    redirect += b"Location: " + location + b"\r\n\r\n"
    return redirect

def has_block(packet: bytes) -> str | None:
    packet = decode(packet)
    fline = packet.split("\r\n")[0]
    valid_block = re.match(BLOCK_REGEX, fline)
    if valid_block: 
        return valid_block.group(1)

def build_block(token: str) -> bytes:
    block_html = b"HTTP/1.1 200 OK\r\n"
    block_html += b"Content-Type: text/html; charset=utf-8\r\n\r\n"
    block_html += push_args_into_template(token=token)
    return block_html