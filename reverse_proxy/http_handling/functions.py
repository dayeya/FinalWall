"""
Author: Daniel Sapojnikov 2023.
http functions module.
"""
import os
import re
import sys
import asyncio
from socket import socket
from .protocol import HTTPRequest, HTTPSessionResponse

def sys_append_modules() -> None:
    """
    Appends all importent modules into sys_path.
    :returns: None.  
    """
    parent = '.../...'
    module = os.path.abspath(os.path.join(os.path.dirname(__file__), parent))
    sys.path.append(module)

sys_append_modules()
from common.network import (
    safe_send, 
    safe_recv,
    SafeRecv,
    SafeSend
)

END_SUFFIX = b'\r\n\r\n'
    
def has_ending_suffix(payload: bytes) -> bool:
    """
    Checks if a payload has the END suffix.
    :params: payload - http packet.
    :returns: bool.
    """
    return END_SUFFIX in payload

def get_content_length(payload: bytes, default: int=-1) -> int:
    """
    Matches the content-length field of a raw HTTP payload.
    :params: payload - http packet, default - default value if not found.
    :returns: Content-Length field.
    """
    response = HTTPSessionResponse(payload)
    content_length = response.getheader('Content-Length', default)
    return int(content_length)