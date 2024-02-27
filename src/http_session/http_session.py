"""
Author: Daniel Sapojnikov 2023.
"""
import os
import sys
from socket import socket
from http_tools.functions import SearchContext, search_header, contains_body_seperator

parent = '.../...'
module = os.path.abspath(os.path.join(os.path.dirname(__file__), parent))
sys.path.append(module)

from net.network_object import (
    ServerConnection, 
    ClientConnection,
    close_all,
    is_closed
)
from net.aionetwork import safe_send, SafeRecv, Address
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
    @property
    def client_addr(self) -> socket:
        return self.__client.address
    @property
    def server_addr(self) -> socket:
        return self.__server.address
    
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
        
        content_length = search_header(bytes(data), SearchContext.CONTENT_LENGTH)
        while len(data) <= content_length:
            chunk = await self.__server.recv()
            if not self.active():
                return b"", 1
            data.extend(chunk)
            self.__update_seq('server', len(chunk))
        
        if not self.active():
            self.close_session()
        return bytes(data), 0
    
    async def client_recv(self) -> SafeRecv:
        data = bytearray(b'')
        while not contains_body_seperator(data):
            chunk = await self.__client.recv()
            if not self.active():
                return b"", 1
            data.extend(chunk)
            self.__update_seq('server', len(chunk))
            
        if not self.active():
            self.close_session()
        return bytes(data), 0
    
    async def send_to_client(self, payload: bytes) -> None:
        if not self.active():
            self.close_session()
        await safe_send(self.client_sock, payload)
        
    async def send_to_server(self, payload: bytes) -> None:
        if not self.active():
            self.close_session()
        await safe_send(self.server_sock, payload)
    