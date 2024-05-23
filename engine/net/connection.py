from typing import Callable
from dataclasses import dataclass
from .aionetwork import AsyncStream, HostAddress, hash_by_host


@dataclass(slots=True)
class Connection:
    """
    A class representing a connection over the network.
    """
    stream: AsyncStream
    addr: HostAddress

    @property
    def ip(self) -> str:
        return self.addr.ip

    @property
    def port(self) -> int:
        return self.addr.port

    @property
    def hash(self) -> str:
        return hash_by_host(self.ip)

    async def recv_until(self, condition: Callable, args: tuple) -> bytes:
        """
        Recv data until a condition is met.
        The first argument of `condition` is ALWAYS data.

        This function is not a replacement of:

            async for chunk in connection.stream:
                data += chunk

        Instead, Connection.recv_until serves as a conditional recv behavior.
        :return: bytes
        """
        data = b""
        async for chunk in self.stream:
            data += chunk
            if condition(data, *args):
                break
        return data

    async def write(self, data: bytes):
        """
        Writes data to the stream.
        :param data:
        :return:
        """
        await self.stream.write(data)

    def close(self):
        """
        Closes the stream.
        :return:
        """
        self.stream.close()

    def __hash__(self) -> int:
        return hash(repr(self))
