"""
Author: Daniel Sapojnikov 2023.
"""
import os
import sys
from socket import socket
from dataclasses import dataclass, field
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
from common.network import safe_recv, SafeRecv
from common.network_object import (
    ServerConnection, 
    ClientConnection,  
    close_all,
    Address
)

@dataclass(slots=True)
class HTTPSession:
    client_side: ClientConnection
    server_side: ServerConnection
    running: bool = field(default_factory=True)
    
    def get_target_sock(self) -> socket:
        return self.server_side.sock
    
    def get_client_sock(self) -> socket:
        return self.client_side.sock
    
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

    def recv_from_target(self) -> bytes:
        """
        Returns a recieved HTTP fragment from target. (maybe  a full HTTP payload)
        """
        fragment, result = safe_recv(self.server_side.sock, buffer_size=8192)
        if not result:
            self.close_session()
            close_all(self.client_side, self.server_side)
        return fragment
        
    def recv_from_client(self) -> bytes:
        """
        Returns a recieved HTTP fragment. (maybe a full HTTP payload)
        """
        fragment, result = safe_recv(self.client_side.sock, buffer_size=8192)
        if not result:
            self.close_session()
            close_all(self.client_side, self.server_side)
        return fragment
    
    def recv_full_http(self, from_target=True) -> SafeRecv:
        """
        Receive a complete HTTP packet regarding fragmentation process.
        :params: sock, buffer.
        :returns: SafeRecv (definition at network.py)
        """
        recv_func = self.recv_from_target if from_target else self.recv_from_client
        
        data = bytearray(recv_func())
        if not self.active():
            return b"", 0
        
        fragments_len = len(data)
        content_length = get_content_length(data, default=-1)
        
        while fragments_len <= content_length:
            data.extend(recv_func())
            if not self.active():
                return b"", 0
            fragments_len = len(data)
            
        return bytes(data), 1