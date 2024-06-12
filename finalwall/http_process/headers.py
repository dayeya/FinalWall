#
# FinalWall - A header for easier header management.
# Author: Dayeya
#

from enum import Enum
from typing import Iterable


class Header(Enum):
    """
    Defines all http used in the engine in *bytes*
    """
    HOST = "Host"
    CONTENT_LENGTH = "Content-Length"
    USER_AGENT = "User-Agent"
    XFF = "X-Forwarded-For"
    PROXY_CONNECTION = "Proxy-Connection"

    def inside(self, headers: Iterable):
        return self.value in headers
