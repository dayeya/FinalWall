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
        
class HTTPServerResponse(HTTPResponse):
    """
    Basic Wrapper to a http response for parsing and using raw bytes.
    """
    def __init__(self, packet: bytes) -> None:
        """
        configuration of HTTPServerResponse.
        """
        self._chunk = packet.split(b'\r\n\r\n', 1)[0]
        self.__bytes_file = BytesSocket(self._chunk)
        
        super().__init__(self.__bytes_file)
        self.begin()