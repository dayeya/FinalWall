"""
Author: Daniel Sapojnikov 2023.
"""
import os
import sys
from socket import socket
from typing import Union, Callable, Dict
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
    ConnectionType,
    close_all,
    conn_to_str
)
class HTTPSession:
    """
    This class defines an HTTP session that is intercepted by the Picky proxy.
    """
    def __init__(self, client: ClientConnection, server: ServerConnection) -> None:
        self.__client = client
        self.__server = server
        self.__running = True
        self.__bytes_sent: Dict[str, bytes] = {'client': 0,'server': 0}
        
    def __identify_sock(self, target: ConnectionType) -> socket:
        """
        Returns the proper socket based on ConnectionType.
        """
        if isinstance(target, ClientConnection):
            return self.get_client_sock()
        return self.get_server_sock()
        
    def get_server_sock(self) -> socket:
        return self.__server.sock
    
    def get_client_sock(self) -> socket:
        return self.__client.sock
    
    def close_session(self) -> None:
        """
        Closes the session.
        """
        self.__running = False
        close_all(self.__client, self.__server)
        
        print("[+] Closed session!")
    
    def active(self) -> bool:
        """
        Returns boolean stating if the session is up or not.
        """
        return self.__running

    def recv_from(self, target: ConnectionType) -> bytes:
        """
        Receives HTTP data from 'target'.
        :params: target - identifier of a target.
        :returns: HTTP data bytes.
        """
        sock = self.__identify_sock(target)
        data, result = safe_recv(sock, buffer_size=8192)
        if not result:
            self.close_session()
        
        self.__bytes_sent[conn_to_str(target)] += len(data)
        return data
    
    def recv_full_http(self, from_server=True) -> SafeRecv:
        """
        Receive a complete HTTP packet regarding dataation process.
        :params: sock, buffer.
        :returns: SafeRecv (definition at network.py)
        """
        target = self.__server if from_server else self.__client
        data = bytearray(self.recv_from(target))

        if not self.active():
            return b"", 0
        
        if not from_server:
            return bytes(data), 1
        
        full_len = len(data)
        response = HTTPResponse(to_bytes(data))
        content_length = get_content_length(response, default=-1)
        
        while full_len <= content_length:
            data.extend(self.recv_from(target))
            if not self.active():
                return b"", 0
            full_len = len(data)
            
        return bytes(data), 1