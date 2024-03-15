"""
Author: Daniel Sapojnikov, 2023.
The asyncio Network module provides simple async networking capabilities.
"""

import asyncio
from socket import socket
from threading import Thread
from typing import Tuple, Callable, Union

# Universal networking constants.
null_ip = "0.0.0.0"
loop_back = '127.0.0.1'
Address = Tuple[str, int]

type Safe_Send_Result = int
type Safe_Recv_Result = Tuple[bytes, int]
type FunctionResult = Union[Safe_Send_Result, Safe_Recv_Result]

def __safe_socket_operation(func: Callable, sock: socket, *args: tuple) -> FunctionResult:
    """
    Wrapper function to perform any socket operation.
    :return: Result of the operation.
    """
    try:
        return func(sock, *args)
    except Exception as e:
        print(f"Error while: {func.__name__} on socket: {sock.getsockname()}, {e}")

async def safe_recv(sock: socket, buffer_size: int) -> Safe_Recv_Result:
    """
    Waits for data from sock.
    :return: decoded data.
    """
    async def recv_wrapper(sock: socket, loop: asyncio.AbstractEventLoop, buffer: int) -> Safe_Recv_Result:
        try:
            data = await loop.sock_recv(sock, buffer)
        except asyncio.IncompleteReadError:
            return b"", 1
            
        if len(data) == buffer:
            while True:
                try:
                    data += await loop.sock_recv(sock, buffer)
                except asyncio.IncompleteReadError:
                    break
        return data, 0

    loop = asyncio.get_event_loop()
    return await __safe_socket_operation(recv_wrapper, sock, loop, buffer_size)

async def safe_send(sock: socket, payload: bytes) -> None:
    """
    Sends a payload from sock.
    :return: None.
    """
    async def send_wrapper(sock: socket, loop: asyncio.AbstractEventLoop, payload: bytes) -> Safe_Send_Result:
        return await loop.sock_sendall(sock, payload)
    
    loop = asyncio.get_event_loop()
    await __safe_socket_operation(send_wrapper, sock, loop, payload)

async def safe_send_recv(sock: socket, payload: str) -> str:
    """
    Sends a payload from sock and waits for an answer, using a safe operation.
    :return: Decoded answer.
    """
    await safe_send(sock, payload)
    data = await safe_recv(sock)
    return data
    
def create_new_thread(func: Callable, *args: tuple) -> Thread:
    """
    Creates a local thread.
    :returns: Thread.
    """
    return Thread(target=func, args=args)

def create_new_task(task_name:str, task: Callable, args: tuple) -> asyncio.Task:
    """
    Creates a new task.
    :returns: Task.
    """
    return asyncio.create_task(name=task_name, coro=task(*args))
