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
    def client_addr(self) -> Address:
        return self.__client.address
    @property
    def server_addr(self) -> Address:
        return self.__server.address
    
    def close_session(self) -> None:
        close_all(self.__client, self.__server)
    
    def active(self) -> bool:
        return is_closed(self.client_sock) or is_closed(self.server_sock)
    
    async def server_recv(self) -> SafeRecv:
        data = b""
        chunk = b""
        while not contains_body_seperator(data):
            chunk = await self.__server.recv()
            if not chunk: 
                break
            data += chunk
        
        print(data)
        
        content = b""
        content_length = int(search_header(data, SearchContext.CONTENT_LENGTH))
        while not len(content) >= content_length:
            chunk = await self.__server.recv()
            if not chunk: 
                break
            content += chunk
        
        print(content)
        if not self.active():
            self.close_session()
            
        response = data + content
        return response, 0
    
    async def client_recv(self) -> SafeRecv:
        data = b""
        while not contains_body_seperator(data):
            chunk = await self.__client.recv()
            if not chunk: 
                break
            data += chunk
            
        if not self.active():
            self.close_session()
        return data, 0
    
    async def send_to_client(self, payload: bytes) -> None:
        if not self.active():
            self.close_session()
        await safe_send(self.client_sock, payload)
        
    async def send_to_server(self, payload: bytes) -> None:
        if not self.active():
            self.close_session()
        await safe_send(self.server_sock, payload)
    