"""
Author: Daniel Sapojnikov 2023.
General HTTP objects to use.
"""

from io import BytesIO
from http.client import HTTPResponse
from http.server import BaseHTTPRequestHandler

class BytesSocket:
    """
    Basic BytesIO socket wrapper.
    """
    def __init__(self, payload_bytes: bytes) -> None:
        """
        __init__ for wrapping BytesIO.
        """
        self._file = BytesIO(payload_bytes)
        
    def makefile(self, *args, **kwargs) -> BytesIO:
        """
        'Override' like function of socket.makefile()
        Return the underlying BytesIO object.
        """
        return self._file

class HTTPRequest(BaseHTTPRequestHandler):
    """
    Basic Wrapper to a http request for parsing and using raw bytes.
    """
    def __init__(self, raw_packet: bytes):
        """
        Http request parser.
        """
        self._chunk = raw_packet
        self.__bytes_file = BytesSocket(self._chunk)

        super().__init__(self.__bytes_file)
        self.parse_request()
        
class HTTPSessionResponse(HTTPResponse):
    """
    Basic parser to a HTTP response from raw bytes.
    """
    def __init__(self, packet: bytes) -> None:
        """
        Http response parser.
        """
        self._chunk = packet.split(b'\r\n\r\n', 1)[0]
        self.__bytes_file = BytesSocket(self._chunk)
        
        super().__init__(self.__bytes_file)
        self.begin()