from typing import Union
from dataclasses import dataclass, field
from urllib.parse import ParseResultBytes
from src.net.aionetwork import HostAddress
from src.http_process.process import process_request_line, process_headers_and_body, process_query


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
    Creates a Transaction object representing each event in the system.
    Notes:
        real_host_address - `True-Client-IP`, refers to the TRUSTED source of the packet.
        has_proxies - If the packet was forwarded through proxies.
        *BOTH* are evaluated at Inspection time (Checker).
    """
    owner: HostAddress
    real_host_address: Union[HostAddress, None]
    has_proxies: bool
    creation_date: str
    raw: bytes
    side: int
    id: int = 0
    method: bytes = Method.GET
    url: ParseResultBytes = None
    version: bytes = b""
    query_params: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)
    body: bytes = b""
    
    def process(self) -> None:
        self.__process_request_line()
        self.__process_message()
        self.__process_params()
    
    def __process_request_line(self) -> None:
        self.method, self.url, self.version = process_request_line(self.raw)

    def __create_transaction_id(self) -> None:
        self.id = hash(repr(self))
    
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
        """
        if self.method == Method.GET:
            self.query_params = process_query(self.url.query)
        if self.method == Method.POST:
            body_params = process_query(self.body)
            query_params = process_query(self.url.query)
            self.query_params = body_params | query_params
        if self.method == Method.PUT:
            raise NotImplementedError
        if self.method == Method.DELETE:
            raise NotImplementedError
        if self.method == Method.HEAD: 
            raise NotImplementedError
        if self.method == Method.TRACE:
            raise NotImplementedError
        if self.method == Method.OPTIONS:
            raise NotImplementedError
