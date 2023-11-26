from typing import Tuple
from socket import socket
from dataclasses import dataclass

Address = Tuple[str, int]

@dataclass(slots=True)
class Client:
    sock: socket
    addr: tuple

    def __init__(self, endpoint: Tuple[socket, Address]) -> None:
        super().__init__(**endpoint)
    
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
        return f'SimpleClient(sock={self.sock}, addr={self.addr})'