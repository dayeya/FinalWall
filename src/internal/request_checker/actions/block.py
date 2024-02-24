# Simple file that defines the behavior of a block.

import re
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from conversion import encode, decode

def _templates_path() -> Path:
    templates_path = Path(__file__).parent.joinpath("templates")
    return templates_path

def _join_templates_path(location: str) -> str:
    parent = Path(__file__).parent.joinpath("templates")
    location = str(parent.joinpath(location))
    return location

def _create_environment() -> Environment:
    try:
        templates_path = _templates_path()
        templates_loader = FileSystemLoader(templates_path)
        env = Environment(loader=templates_loader)
        listed = env.list_templates()
        print(listed)
        return env
    except Exception as e:
        print("Unable to create environment due:", e)
        raise e

ENV = _create_environment()
SECURITY_PAGE = "security_page.html"
BLOCK_REGEX = re.compile(r"GET /block[?]token=([a-z0-9]{8})")
    
def _push_args_into_template(activity_token: str) -> bytes:
    block_template = ENV.get_template(SECURITY_PAGE)
    parsed_template = block_template.render(token=activity_token)
    return parsed_template.encode("utf-8")

def build_block(token: str) -> bytes:
    block_html = b"HTTP/1.1 200 OK\r\n"
    block_html += b"Content-Type: text/html; charset=utf-8\r\n\r\n"
    block_html += _push_args_into_template(token)
    print(block_html)
    return block_html

def build_redirect(location: bytes) -> bytes:
    redirect = b"HTTP/1.1 302 Found\r\n"
    redirect += b"Location: " + location + b"\r\n\r\n"
    return redirect

def contains_block(packet: bytes) -> str | None:
    packet = decode(packet)
    fline = packet.split("\r\n")[0]
    valid_block = re.match(BLOCK_REGEX, fline)
    if valid_block: 
        return valid_block.group(1)