from urllib.parse import ParseResult
from dataclasses import dataclass, field
from http_tools.tools import PARAM_START
from http_tools.tools import process_request_line, process_headers_and_body, process_query

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
    TODO: Identify escape sequences e.g. SEL\bLECT = SELECT
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
    url: ParseResult = None
    version: bytes = b""
    params: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)
    body: bytes = b""
    
    def process(self) -> None:
        self.__process_request_line()
        self.__process_message()
        self.__process_params()
    
    def __process_request_line(self) -> None:
        self.method, self.url, self.version = process_request_line(self.raw)
    
    def __create_transaction_id(self) -> None:
        # TODO: Create a unique transaction id based on some parameters.
        pass
    
    def __process_message(self) -> None:
        self.headers, self.body = process_headers_and_body(self.raw)
    
    def __process_headers(self) -> None:
        """
        Processes all the headers and decodes them if needed.
        """
        pass
        
    def __process_body(self) -> None:
        """
        Processes the body and decodes it if needed.
        """
        pass
    
    def __process_params(self) -> None:
        """
        Processes the params either of the URL or the body.
        TODO: Parse the data before processing it.
        """
        if self.method == Method.GET:
            self.params = process_query(self.url.params)
        if self.method == Method.POST:
            self.params = process_query(self.body)
        if self.method == Method.PUT:
            assert False, "Not implemented."
        if self.method == Method.DELETE:
            assert False, "Not implemented."
        if self.method == Method.HEAD: 
            assert False, "Not implemented."
        if self.method == Method.TRACE:
            assert False, "Not implemented."
        if self.method == Method.OPTIONS:
            assert False, "Not implemented."