import asyncio
from socket import socket
from dataclasses import dataclass
from src.net.aionetwork import safe_send, safe_recv, HostAddress


@dataclass(slots=True)
class Connection:
    sock: socket
    addr: HostAddress

    async def establish(self):
        """
        Establish the connection completely, this happens after __init__.
        """
        try:
            loop = asyncio.get_event_loop()
            await loop.sock_connect(self.sock, self.addr.tuplize())
        except OSError:
            print(f"ERROR: Could not establish connection with {self.addr}")

    def close(self) -> None:
        self.sock.close()

    async def recv(self) -> bytes:
        data, err = await safe_recv(self.sock, buffer_size=8192)
        if err:
            self.close()
        return data

    async def send(self, data: bytes) -> None:
        await safe_send(self.sock, data)

    def __hash__(self) -> int:
        return hash((self.sock, self.addr))
