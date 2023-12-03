import asyncio
from abc import ABC, abstractmethod

class HTTPService(ABC):
    """
    Base HTTPHandler class to inherit from.
    Provides special functions to use across the HTTP protocol.
    """
    def __init__(self) -> None:
        pass
    
    @abstractmethod
    def recv_http(self) -> None:
        pass
    
    @abstractmethod
    def forward_http(self) -> None:
        pass