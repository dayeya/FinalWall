from typing import Union
from dataclasses import dataclass, field
from urllib.parse import ParseResultBytes
from engine.net.aionetwork import HostAddress
from engine.http_process.process import process_request_line, process_headers_and_body, process_query


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

    Attributes
    ----------
    owner - host that sent the transaction in its raw form.
    real_host_address - Some may know it as True-Client-IP, refers to the TRUSTED source of the transaction.
    raw - Raw bytes of the request.
    creation_date - The date where the transaction was processed by the WAF.
    method - HTTP method.
    url - URL including params.
    version - HTTP version.
    query_params - Dictionary of the queries and their values.
    headers - Dictionary of headers and their values.
    body - Body of the raw bytes of the transaction.
    """
    owner: HostAddress
    real_host_address: Union[HostAddress, None]
    raw: bytes
    creation_date: str
    method: bytes = Method.GET
    url: ParseResultBytes = None
    version: bytes = b""
    query_params: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)
    body: bytes = b""
    size: int = 0

    @property
    def hash(self) -> int:
        return hash(repr(self))

    def process(self) -> None:
        self.__process_request_line()
        self.__process_message()
        self.__process_params()
    
    def __process_request_line(self) -> None:
        self.method, self.url, self.version = process_request_line(self.raw)
    
    def __process_message(self) -> None:
        self.headers, self.body = process_headers_and_body(self.raw)
    
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
