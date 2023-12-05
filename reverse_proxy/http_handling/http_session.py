"""
Author: Daniel Sapojnikov 2023.
HTTP session.
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
from common.network_object import Client, Address

# ============================================================
# http session object, defines behaviour of a regular session.
# ============================================================

@dataclass(slots=True)
class HTTPSession:
    running: bool = field(default_factory=True)
    client_side: Client
    target_side: Address
    
    def close_session(self) -> None:
        pass
    
    def is_on(self) -> bool:
        """
        Returns boolean stating if the session is up or not.
        """
        return self.running

    def recv_fragment(self) -> SafeRecv:
        """
        Returns a recieved HTTP fragment. (maybe a full HTTP payload)
        """
        fragment, result = safe_recv(self.client_side.sock, buffer_size=8192)
        if not result:
            self.cclose_session()
        return fragment
    
    def full_http_packet(self) -> SafeRecv:
        """
        Receive a complete HTTP packet regarding fragmentation process.
        :params: sock, buffer.
        :returns: SafeRecv (definition at network.py)
        """
        data = bytearray(self.recv_fragment())
        if not self.is_on():
            return b"", 0
        
        fragments_len = len(data)
        content_length = get_content_length(data, default=-1)
        
        while fragments_len <= content_length:
            data.extend(self.recv_fragment())
            if not self.is_on():
                return b"", 0
            fragments_len = len(data)
            
        return bytes(data), 1