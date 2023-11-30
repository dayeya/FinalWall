"""
Author: Daniel Sapojnikov 2023.
Client Class used to define clients across the LAN.
"""

from typing import Tuple
from socket import socket
from dataclasses import dataclass

Address = Tuple[str, int]
Endpoint = Tuple[socket, Address]

@dataclass
class Client:
    sock: socket
    addr: tuple
    
    __slots__ = ('sock', 'addr')

    @property
    def port(self) -> str:
        """
        Getter for the port address.
        :returns: port of the client.
        """
        return self.addr[1]

    @property
    def ip(self) -> str:
        """
        Getter for the ip address.
        :returns: ip of the client.
        """
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