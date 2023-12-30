# Simple file that defines the behavior of a BLOCK.

from pathlib import Path
from jinja2 import Environment

BASE_FILE = __file__
HTML_FILE = "block.html"
STYLES_FILE = "main.css"
ENV = Environment()

def abs_component_path(location: str) -> str:
    parent = Path(BASE_FILE).parent.joinpath('page')
    location  = str(parent.joinpath(location))
    return location

def abs_html_path() -> str:
    return abs_component_path(HTML_FILE)

def abs_css_path() -> str:
    return abs_component_path(STYLES_FILE)

def push_args_into_template(*args, **kwargs) -> str:
    html_file = abs_html_path()
    with open(html_file, 'r') as h:
        html = h.read()
    block_template = ENV.from_string(html)
    
    # Update the HTML file.
    with open(html_file, "w", encoding="utf-8") as block:
        block.write(block_template.render(*args, **kwargs))
        
def push_styles() -> None:
    with open(abs_css_path(), "rb") as s:
        return s.read()

def build_page(token: str) -> None:
    """Builds the block page with custom arguments."""
    
    block_html = b"HTTP/1.1 403 Forbidden\r\n"
    block_html += b"Content-Type: text/html; charset=utf-8\r\n\r\n"
    push_args_into_template(token=token)
    
    with open(abs_html_path(), "rb") as block:
        block_html += block.read()
    return block_html

def build_styles() -> None:
    block_styles = b"HTTP/1.1 200 \r\n"
    block_styles += b"Content-Type: text/css\r\n\r\n"
    block_styles += push_styles()
    return block_styles