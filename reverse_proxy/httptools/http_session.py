"""
Author: Daniel Sapojnikov 2023.
"""
import os
import sys
from socket import socket
from typing import Union, Callable
from dataclasses import dataclass, field
from .protocol import HTTPSessionResponse as HTTPResponse
from .functions import get_content_length

def sys_append_modules() -> None:
    """
    Appends all importent modules into sys_path.
    :returns: None.  
    """
    parent = '.../...'
    module = os.path.abspath(os.path.join(os.path.dirname(__file__), parent))
    sys.path.append(module)

sys_append_modules()
from common.conversion import to_bytes
from common.network import safe_recv, SafeRecv
from common.network_object import (
    ServerConnection, 
    ClientConnection,  
    close_all,
    Address
)

type Target = Union[ClientConnection, ServerConnection]

@dataclass(slots=True)
class HTTPSession:
    """
    This class defines an HTTP session that is intercepted by the Picky proxy.
    """
    client_side: ClientConnection
    server_side: ServerConnection
    running: bool = field(default_factory=False)
    
    def get_server_sock(self) -> socket:
        return self.server_side.sock
    
    def get_client_sock(self) -> socket:
        return self.client_side.sock
    
    def __identify_sock(self, target: Target) -> socket:
        """
        Returns the proper socket based on the targets type.
        """
        if isinstance(target, ClientConnection):
            return self.get_client_sock()
        return self.get_server_sock()
    
    def close_session(self) -> None:
        """
        Closes the session.
        """
        self.running = False
        close_all(self.client_side, self.server_side)
    
    def active(self) -> bool:
        """
        Returns boolean stating if the session is up or not.
        """
        return self.running

    def recv_from(self, target: Target) -> bytes:
        """
        Receives HTTP data from 'target'.
        :params: target - identifier of a target.
        :returns: HTTP data bytes.
        """
        sock = self.__identify_sock(target)
        data, result = safe_recv(sock, buffer_size=8192)
        if not result:
            self.close_session()
            close_all(self.client_side, self.server_side)
        return data
    
    def recv_full_http(self, from_server=True) -> SafeRecv:
        """
        Receive a complete HTTP packet regarding dataation process.
        :params: sock, buffer.
        :returns: SafeRecv (definition at network.py)
        """
        target = self.server_side if from_server else self.client_side
        data = bytearray(self.recv_from(target))
                 
        if not self.active():
            return b"", 0
        
        if not from_server:
            return bytes(data), 1
        
        response = HTTPResponse(to_bytes(data))
        full_len = len(data)
        content_length = get_content_length(response, default=-1)
        
        while full_len <= content_length:
            data.extend(self.recv_from(target))
            if not self.active():
                return b"", 0
            full_len = len(data)
            
        return bytes(data), 1