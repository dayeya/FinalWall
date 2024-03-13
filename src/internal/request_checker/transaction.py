from dataclasses import dataclass, field
from typing import Optional
from http_tools.tools import unpack_request_line

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
    id: str = ""
    method: bytes = Method.GET
    uri: bytes = b""
    version: bytes = b""
    body: bytes = b""
    params: dict = field(default_factory=dict)
    
    def process(self) -> None: 
        # TODO: Process each part of the transaction.
        self.__process_request_line()
    
    def __process_request_line(self) -> None:
        self.method, self.uri, self.version = unpack_request_line(self.raw)
    
    def __create_transaction_id(self) -> None:
        # TODO: Create a unique transaction id based on some parameters.
        pass
    
    def __process_headers(self) -> None:
        # TODO: Create a dictionary of headrs from the transaction.
        pass