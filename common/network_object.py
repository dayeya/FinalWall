"""
Author: Daniel Sapojnikov 2023.
Client Class used to define clients across the LAN.
"""

from socket import socket
from typing import Tuple, Union
from dataclasses import dataclass

type Address = Tuple[str, int]

@dataclass
class Client:
    sock: socket
    addr: Address
    
    __slots__ = ('sock', 'addr')

    @property
    def port(self) -> str:
        return self.addr[1]

    @property
    def ip(self) -> str:
        return self.addr[0]

    def close(self) -> None:
        """
        Closes the socket.
        :returns: None.
        """
        self.sock.close()
    
    def __repr__(self) -> str:
        """
        Crafts a str from a client.
        :returns: Simplified string.
        """
        return f'Client(sock={self.sock}, addr={self.addr})'

type NetworkObject = Union[Client, socket]

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