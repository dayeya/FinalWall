"""
Author: Daniel Sapojnikov, 2023.
Network module contains useful function related to networking.
"""

import sys
from socket import *
from typing import Callable, Union
from threading import Thread
from .conversion import decode, encode

# Universal networking constants.
all_interfaces = "0.0.0.0"
listen_bound = 5

# Custom types.
FunctionResult = Union[bytes, None]

def __safe_socket_operation(func: Callable, sock: socket, *args: tuple) -> FunctionResult:
    """
    Wrapper function to perform any socket operation.
    :params: func, sock, args.
    :return: Result of the operation.
    """
    try:
        return func(sock, *args)
    except Exception as e:
        print(f"Error while: {func.__name__} on socket: {sock.getsockname()}, {e}")

def safe_recv(sock: socket, buffer_size: int) -> str:
    """
    Waits for data from sock.
    :params: sock, buffer_size.
    :return: decoded data.
    """
    def __recv(sock: socket, buffer: int) -> bytes:
        return sock.recv(buffer)
    
    return decode(__safe_socket_operation(__recv, sock, buffer_size))

def safe_send(sock: socket, payload: str) -> None:
    """
    Sends a payload from sock.
    :params: sock, payload.
    :return: None.
    """
    def __send(sock: socket, payload: str) -> bytes:
        return sock.send(encode(payload))
    
    __safe_socket_operation(__send, sock, payload)

def safe_send_recv(sock: socket, payload: str) -> str:
    """
    Sends a payload from sock and waits for an answer, using a safe operation.
    :params: sock, payload.
    :return: Decoded answer.
    """
    safe_send(sock, payload)
    data = safe_recv(sock)
    return data
    
def create_new_thread(func: Callable, *args: tuple) -> Thread:
    """
    Creates a local thread.
    :params: func, args.
    :returns: Thread.
    """
    return Thread(target=func, args=args)
