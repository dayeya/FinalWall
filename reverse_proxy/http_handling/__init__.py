"""
Simple module for the HTTP protocol.
"""
from .protocol import HTTPRequest, HTTPSessionResponse
from .functions import get_content_length, recv_http