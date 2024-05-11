from enum import Enum


class Header(Enum):
    """
    Defines all http used in the engine in *bytes*
    """
    HOST = b"Host"
    CONTENT_LENGTH = b"Content-Length"
    USER_AGENT = b"User-Agent"
    XFF = b"X-Forwarded-For"
    PROXY_CONNECTION = b"Proxy-Connection"

    def __contains__(self, header_collection):
        return self.name in header_collection
