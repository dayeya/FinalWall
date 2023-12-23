"""
Author: Daniel Sapojnikov 2023.
"""
from io import BytesIO
from http.client import HTTPResponse
from http.server import BaseHTTPRequestHandler

class BytesSocket:
    """
    Basic BytesIO socket wrapper.
    """
    def __init__(self, payload_bytes: bytes) -> None:
        self._file = BytesIO(payload_bytes)
        
    def makefile(self, *args, **kwargs) -> BytesIO:
        """
        'Override' like function of socket.makefile()
        :returns: the underlying BytesIO object.
        """
        return self._file

class HTTPRequestParser(BaseHTTPRequestHandler):
    def __init__(self, raw_packet: bytes) -> None:
        self._chunk = raw_packet
        self.__bytes_file = BytesSocket(self._chunk)

        super().__init__(self.__bytes_file)
        self.parse_request()
        
class HTTPResponseParser(HTTPResponse):
    """
    HTTP response parser.
    """
    def __init__(self, packet: bytes) -> None:
        self._chunk = packet.split(b'\r\n\r\n', 1)[0]
        self.__bytes_file = BytesSocket(self._chunk)
        
        super().__init__(self.__bytes_file)
        self.begin()
    
    def get_packet(self) -> bytes:
        return self._chunk