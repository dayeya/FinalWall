# Simple file that defines the behavior of a block.

import re
from pathlib import Path
from conversion import encode
from urllib.parse import urlunparse
from jinja2 import Environment, FileSystemLoader
from internal.system.transaction import Transaction, Method

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
        _ = env.list_templates()
        return env
    except Exception as e:
        print("Unable to create environment due:", e)
        raise e

ENV = _create_environment()
SECURITY_PAGE = "security_page.html"
BLOCK_REGEX = re.compile(r"/block[?]token=([a-z0-9]{8})")
    
def _push_args_into_template(activity_token: str) -> bytes:
    block_template = ENV.get_template(SECURITY_PAGE)
    parsed_template = block_template.render(token=activity_token)
    return parsed_template.encode("utf-8")

def build_block(token: str) -> bytes:
    security_page: bytes = _push_args_into_template(token)
    block_html = b"HTTP/1.1 200 OK\r\n"
    block_html += b"Content-Type: text/html; charset=utf-8\r\n"
    block_html += b"Content-Length: " + encode(str(len(security_page))) + b"\r\n"
    block_html += b"Connection: close\r\n\r\n"
    block_html += security_page
    return block_html

def build_redirect(location: bytes) -> bytes:
    redirect = b"HTTP/1.1 302 Found\r\n"
    redirect += b"Location: " + location + b"\r\n\r\n"
    return redirect

def contains_block(tx: Transaction) -> str | None:
    resource: bytes = urlunparse(tx.url)
    valid_block: re.Match = re.match(BLOCK_REGEX, resource.decode())
    if tx.method == Method.GET and valid_block: 
        return valid_block.group(1)
    
    
    