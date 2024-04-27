"""
Author: Daniel Sapojnikov, 2023.
The asyncio Network module provides simple async networking capabilities.
"""

import asyncio
import ipaddress
import threading
from dataclasses import dataclass
from typing import Tuple, Callable, Union, Self

type Network_Address = Tuple[Union[ipaddress.IPv4Address, ipaddress.IPv6Address], int]

REMOTE_ADDR = "peername"
SOCKET = "socket"
SOCKNAME = "sockname"


@dataclass(slots=True)
class HostAddress:
    ip: str
    port: int


class AsyncStream:
    _BUFFER_SIZE = 8192

    def __init__(self, reader: asyncio.StreamReader=None, writer: asyncio.StreamWriter=None):
        self.__reader = reader
        self.__writer = writer

    async def write(self, data: bytes):
        self.__writer.write(data)
        await self.__writer.drain()

    async def close(self):
        self.__writer.close()
        await self.__writer.wait_closed()

    @classmethod
    async def open_stream(cls, ip: str, port: int) -> Self:
        try:
            reader, writer = await asyncio.open_connection(host=ip, port=port)
            return cls(reader, writer)
        except OSError:
            print("ERROR: could not connect to the server")
            return cls(None, None)

    def __aiter__(self):
        return self

    async def __anext__(self) -> bytes:
        data = await self.__reader.read(n=AsyncStream._BUFFER_SIZE)
        if not data:
            raise StopAsyncIteration
        return data


def create_new_thread(func: Callable, args: tuple, daemon: bool) -> threading.Thread:
    """
    Creates a local thread.
    :returns: Thread.
    """
    return threading.Thread(target=func, args=args, daemon=daemon)


def create_new_task(task_name: str, task: Callable, args: tuple) -> asyncio.Task:
    """
    Creates a new task.
    :returns: Task.
    """
    return asyncio.create_task(name=task_name, coro=task(*args))


def convert_netloc(netloc: str) -> Union[Network_Address, None]:
    try:
        ip, sep, port = netloc.rpartition(":")
        assert sep, AssertionError
        return ipaddress.ip_address(ip), int(port)

    except AssertionError:
        # No port was specified.
        try:
            return ipaddress.ip_address(netloc), -1
        except ValueError:
            return None

    except ValueError:
        return None


__all__ = [
    "HostAddress",
    "AsyncStream",
    "create_new_task",
    "convert_netloc"
]
