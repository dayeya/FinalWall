"""
Author: Daniel Sapojnikov 2023.
"""
import os
import sys
from socket import socket
from typing import Callable, Dict
from http_tools.protocol import HTTPResponseParser as HTTPResponse
from http_tools.functions import get_content_length, has_ending_suffix

def sys_append_modules() -> None:
    """
    Appends all importent modules into sys_path.
    :returns: None.  
    """
    parent = '.../...'
    module = os.path.abspath(os.path.join(os.path.dirname(__file__), parent))
    sys.path.append(module)

sys_append_modules()
from net.aionetwork import (
    safe_recv, 
    SafeRecv,
    Address
)

from net.network_object import (
    ConnectionType,
    ServerConnection, 
    ClientConnection,
    close_all,
    is_closed,
    determine_conn
)

class HTTPSession:
    def __init__(self, client: ClientConnection, server: ServerConnection, proxy: Address) -> None:
        self.__client = client
        self.__server = server
        self.__proxy = proxy
        self.__bytes_sent = {'client': 0,'server': 0}
    
    @property
    def proxy(self) -> Address:
        return self.__proxy
    @property
    def client_seq(self) -> int:
        return self.__bytes_sent['client']
    @property
    def server_seq(self) -> int:
        return self.__bytes_sent['server']
    @property
    def client_sock(self) -> socket:
        return self.__client.sock
    @property
    def server_sock(self) -> socket:
        return self.__server.sock
    
    def close_session(self) -> None:
        close_all(self.__client, self.__server)
    
    def active(self) -> bool:
        return is_closed(self.client_sock) or is_closed(self.server_sock)
    
    def __update_seq(self, sender: str, seq: int) -> None:
        self.__bytes_sent[sender] =+ seq
    
    async def server_recv(self) -> SafeRecv:
        data = bytearray(await self.__server.recv())
        if not self.active():
            return b"", 0
        
        response = HTTPResponse(bytes(data))
        content_length = get_content_length(response, default=-1)
        while len(data) <= content_length:
            chunk = await self.__server.recv()
            if not self.active():
                return b"", 0
            data.extend(chunk)
            self.__update_seq('server', len(chunk))
        
        if not self.active():
            self.close_session()
        return bytes(data), 1
    
    async def client_recv(self) -> SafeRecv:
        data = bytearray(b'')
        while not has_ending_suffix(data):
            chunk = await self.__client.recv()
            if not self.active():
                return b"", 0
            data.extend(chunk)
            self.__update_seq('server', len(chunk))
            
        if not self.active():
            self.close_session()
        return bytes(data), 1
    