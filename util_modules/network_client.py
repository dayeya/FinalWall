from typing import Tuple
from socket import socket
from dataclasses import dataclass

Address = Tuple[str, int]
Endpoint = Tuple[socket, Address]

@dataclass(slots=True)
class Client:
    sock: socket
    addr: tuple
    
    def close(self) -> None:
        """
        Closes the socket.
        """
        self.sock.close()
    
    def __str__(self) -> str:
        """
        Crafts a str from a client.

        Returns:
            str: Simplified string.
        """
        return f'Client(sock={self.sock}, addr={self.addr})'