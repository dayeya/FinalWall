"""
Author: Daniel Sapojnikov 2023.
http functions module.
"""
import re
import asyncio
from .protocol import HTTPRequest, HTTPServerResponse

CHUNK_END = b'\r\n\r\n'
    
def has_ending_suffix(payload: bytes) -> bool:
    pass

def get_content_length(payload: bytes, default: int=-1) -> int:
    """
    Matches the content-length field HTTPResponse.
    :params: payload - http request / response.
    :returns: Content-Length field.
    """
    # Handle default case.
    if not payload:
        return -1
        
    response = HTTPServerResponse(payload)
    content_length = response.getheader('Content-Length', default)
    return int(content_length)
    