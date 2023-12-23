"""
Author: Daniel Sapojnikov 2023.
Client Class used to define clients across the LAN.
"""

from typing import Tuple, Union
from socket import socket, MSG_PEEK
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
        return f'ClientConnection(sock={self.sock}, addr={self.host_addr})'

class ServerConnection(Connection):
    def __init__(self, sock: socket, addr: Address) -> None:
        super().__init__(sock, addr)
        
    def __repr__(self) -> str:
        return f'ServerConnection(sock={self.sock}, addr={self.host_addr})'

type ConnectionType = Union[ClientConnection, ServerConnection]
type NetworkObject = Union[ConnectionType, socket]

def close_all(*objects: Tuple[NetworkObject]) -> None:
    for closable in objects:
        classify = closable.__class__.__name__
        try:
            closable.close()
            print(f'[!] A {classify} object was closed successfuly!')
        except Exception as close_error:
            print(f'[!] {classify}.close() was not complete. {close_error}')
            
def is_closed(object: NetworkObject) -> bool:
    try:
        obj_sock = object.sock if not isinstance(object, socket) else object
        return not bool(obj_sock.recv(1, MSG_PEEK))
    except:
        return True
            
def conn_to_str(conn_type: ConnectionType) -> str:
    """
    Converts the ConnectionType into a string.
    :returns: ClientConnection -> "client", ServerConnection -> "server.
    """
    return repr(conn_type)[:6].lower()