"""
Author: Daniel Sapojnikov 2023.
Client Class used to define clients across the LAN.
"""

from socket import socket
from typing import Tuple, Union
from dataclasses import dataclass

type Address = Tuple[str, int]

@dataclass(slots=True)
class Connection:
    sock: socket
    host_addr: Address

    @property
    def address(self) -> Address:
        return self.host_addr
    
    def close(self) -> None:
        self.sock.close()
        
    def __hash__(self) -> int:
        return hash((self.sock, self.host_addr))

class ClientConnection(Connection):
    def __init__(self, sock: socket, addr: Address) -> None:
        super().__init__(sock, addr)
        
    def __repr__(self) -> str:
        return f'ServerConnection(sock={self.sock}, addr={self.host_addr})'

class ServerConnection(Connection):
    def __init__(self, sock: socket, addr: Address) -> None:
        super().__init__(sock, addr)
        
    def __repr__(self) -> str:
        return f'ServerConnection(sock={self.sock}, addr={self.host_addr})'

type NetworkObject = Union[ServerConnection, ClientConnection, socket]

def close_all(*args: Tuple[NetworkObject]) -> None:
    """
    Closes all network objects that have .close()
    """
    for obj in args:
        classify = obj.__class__.__name__
        try:
            obj.close()
            print(f'[!] A {classify} object was closed successfuly!')
        except Exception as close_error:
            print(f'[!] {classify}.close() was not complete. {close_error}')