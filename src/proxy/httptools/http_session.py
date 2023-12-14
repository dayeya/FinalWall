"""
Author: Daniel Sapojnikov 2023.
"""
import os
import sys
from socket import socket
from abc import ABC, abstractmethod
from typing import Union, Callable, Dict
from dataclasses import dataclass, field
from .protocol import HTTPSessionResponse as HTTPResponse
from .functions import get_content_length, has_ending_suffix

def sys_append_modules() -> None:
    """
    Appends all importent modules into sys_path.
    :returns: None.  
    """
    parent = '.../...'
    module = os.path.abspath(os.path.join(os.path.dirname(__file__), parent))
    sys.path.append(module)

sys_append_modules()
from conversion.conversion import to_bytes
from net.aionetwork.aionetwork import safe_recv, SafeRecv
from net.network_object.network_object import (
    ConnectionType,
    ServerConnection, 
    ClientConnection,
    close_all,
    is_closed,
    conn_to_str
)

class HTTPSession:
    """
    This class defines an HTTP session that is intercepted by the Picky proxy.
    """
    def __init__(self, client: ClientConnection, server: ServerConnection) -> None:
        self.__running = True
        self.__client = client
        self.__server = server
        self.__bytes_sent: Dict[str, bytes] = {'client': 0,'server': 0}
        
    @property
    def client_recv(self) -> Callable:
        return self.__recv_from_client
    @property
    def server_recv(self) -> Callable:
        return self.__recv_from_server
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

    async def recv_from(self, conn: ConnectionType) -> bytes:
        data, result = await safe_recv(conn.sock, buffer_size=8192)
        if not result:
            self.close_session()
        self.__bytes_sent[conn_to_str(conn)] += len(data)
        return data
    
    async def __recv_from_server(self) -> SafeRecv:
        data = bytearray(await self.recv_from(self.__server))
        if not self.active():
            return b"", 0
        
        response = HTTPResponse(to_bytes(data))
        content_length = get_content_length(response, default=-1)
        while len(data) <= content_length:
            data.extend(await self.recv_from(self.__server))
            if not self.active():
                return b"", 0
            
        return to_bytes(data), 1
    
    async def __recv_from_client(self) -> SafeRecv:
        data = bytearray(await self.recv_from(self.__client))
        if not self.active(): 
            return b"", 0
        
        while not has_ending_suffix(data):
            data.extend(await self.recv_from(self.__client))
            if not self.active():
                return b"", 0
            
        return to_bytes(data), 1
    
    async def recv_full_http(self, recv_func: Callable) -> bytes:
        data, _ = await recv_func()
        return data