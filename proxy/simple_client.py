from socket import socket
from dataclasses import dataclass

@dataclass(slots=True)
class SimpleClient:
    sock: socket
    addr: tuple
    
    def __repr__(self) -> str:
        """
        Crafts a str from a client.

        Returns:
            str: Simplified string.
        """
        return f'SimpleClient(sock={self.sock}, addr={self.addr})'
    
    def __str__(self) -> str:
        """
        Crafts a str from a client.

        Returns:
            str: Simplified string.
        """
        return f'socket: {self.sock}, addr: {self.addr}'