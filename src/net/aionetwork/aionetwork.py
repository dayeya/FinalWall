"""
Author: Daniel Sapojnikov, 2023.
The asyncio Network module provides simple async networking capabilities.
"""

import asyncio
import ipaddress
from socket import socket
from threading import Thread
from typing import Tuple, Callable, Union, Optional
from dataclasses import dataclass

type NETWORK_ADDRESS = Tuple[Union[ipaddress.IPv4Address, ipaddress.IPv6Address], int]
type Safe_Send_Result = int
type Safe_Recv_Result = Tuple[bytes, int]
type FunctionResult = Union[Safe_Send_Result, Safe_Recv_Result]

NETLOC_SEP = ":"


@dataclass
class HostAddress:
    ip: str
    port: int

    def tuplize(self):
        tup = (self.ip, self.port)
        return tup


async def safe_recv(sock: socket, buffer_size: int) -> Safe_Recv_Result:
    """
    Waits for data from sock.
    :return: decoded data.
    """
    loop = asyncio.get_event_loop()
    try:
        data = await loop.sock_recv(sock, buffer_size)
    except asyncio.IncompleteReadError:
        return b"", 1

    if len(data) == buffer_size:
        while True:
            try:
                data += await loop.sock_recv(sock, buffer_size)
            except asyncio.IncompleteReadError:
                break
    return data, 0


async def safe_send(sock: socket, data: bytes) -> None:
    """
    Sends a payload from sock.
    :return: None.
    """
    try:
        loop = asyncio.get_event_loop()
        await loop.sock_sendall(sock, data)
    except OSError:
        print(f"ERROR: Could not send data to {sock}")


async def safe_send_recv(sock: socket, payload: bytes) -> bytes:
    """
    Sends a payload from sock and waits for an answer, using a safe operation.
    :return: Decoded answer.
    """
    await safe_send(sock, payload)
    data, err = await safe_recv(sock, buffer_size=8192)
    if err:
        print(f"SOCKET CLOSED {sock.getsockname()}")
    return data


def create_new_thread(func: Callable, *args: tuple) -> Thread:
    """
    Creates a local thread.
    :returns: Thread.
    """
    return Thread(target=func, args=args)


def create_new_task(task_name: str, task: Callable, args: tuple) -> asyncio.Task:
    """
    Creates a new task.
    :returns: Task.
    """
    return asyncio.create_task(name=task_name, coro=task(*args))


def convert_netloc(netloc: str) -> Union[NETWORK_ADDRESS, None]:
    try:
        ip, sep, port = netloc.rpartition(NETLOC_SEP)
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
