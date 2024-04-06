import asyncio
from typing import Tuple
from socket import socket, AF_INET, SOCK_STREAM
from dataclasses import dataclass
from src.net.aionetwork import safe_send, safe_recv, Safe_Recv_Result

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

    async def recv(self) -> Safe_Recv_Result:
        data, err = await safe_recv(self.sock, buffer_size=8192)
        if err:
            self.close()
        return data

    async def send(self, data: bytes) -> None:
        await safe_send(self.sock, data)


async def establish_connection(target: Address) -> Connection:
    try:
        loop = asyncio.get_event_loop()
        sock = socket(AF_INET, SOCK_STREAM)
        await loop.sock_connect(sock, target)
        return Connection(sock, target)
    except OSError as _e:
        print(f"ERROR: Could not connect to {target}")