from dataclasses import dataclass, field
from http_tools.tools import process_request_line, process_headers_and_body

SERVER_RESPONSE = 0
CLIENT_REQUEST = 1

class Method:
    GET = b"GET"
    POST = b"POST"
    PUT = b"PUT"
    DELETE = b"DELETE"
    HEAD = b"HEAD"
    TRACE = b"TRACE"
    CONNECT = b"CONNECT"
    OPTIONS = b"OPTIONS"

class Parser:
    """
    Normalizes data encoded in different methods. 
    """
    
@dataclass(slots=True)
class Transaction:
    """
    Creates a signature of each HTTP request.
    """
    raw: bytes
    side: int
    id: str = ""
    method: bytes = Method.GET
    uri: bytes = b""
    params: dict = field(default_factory=dict)
    version: bytes = b""
    headers: dict = field(default_factory=dict)
    body: bytes = b""
    
    def process(self) -> None:
        self.__process_request_line()
        self.__process_message()
    
    def __process_request_line(self) -> None:
        self.method, self.uri, self.version = process_request_line(self.raw)
    
    def __create_transaction_id(self) -> None:
        # TODO: Create a unique transaction id based on some parameters.
        pass
    
    def __process_message(self) -> None:
        self.headers, self.body = process_headers_and_body(self.raw)
    
    def __process_headers(self) -> None:
        pass
        
    def __process_body(self) -> None:
        pass