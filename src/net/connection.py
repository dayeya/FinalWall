from typing import Callable
from dataclasses import dataclass
from src.net.aionetwork import AsyncStream, HostAddress


@dataclass(slots=True)
class Connection:
    stream: AsyncStream
    addr: HostAddress

    async def recv_until(self, condition: Callable, args: tuple) -> bytes:
        """
        Recv data until a condition is met.
        The first argument of `condition` is ALWAYS data.

        This function is not a replacement of:

            async for chunk in connection.stream:
                data += chunk

        Instead, Connection.recv_until serves as a conditional recv behaviour.
        """
        data = b""
        async for chunk in self.stream:
            data += chunk
            if condition(data, *args):
                break
        return data

    async def write(self, data: bytes) -> None:
        await self.stream.write(data)

    def close(self) -> None:
        self.stream.close()

    def __hash__(self) -> int:
        return hash(repr(self))
