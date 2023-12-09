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

END_SUFFIX = b'\r\n\r\n'
    
def has_ending_suffix(payload: bytes) -> bool:
    return END_SUFFIX in payload

def get_content_length(response: HTTPSessionResponse, default: int=-1) -> int:
    content_length = response.getheader('Content-Length', default)
    return int(content_length)