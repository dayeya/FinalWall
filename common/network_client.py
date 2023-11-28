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

    def close(self) -> None:
        """
        Closes the socket.
        :returns: None.
        """
        self.sock.close()
    
    def __str__(self) -> str:
        """
        Crafts a str from a client.
        :returns: Simplified string.
        """
        return f'Client(sock={self.sock}, addr={self.addr})'