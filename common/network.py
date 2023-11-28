"""
Author: Daniel Sapojnikov, 2023.
Network module contains useful function related to networking.
"""

import sys
from socket import *
from typing import Callable, Union
from threading import Thread
from .network_client import Client
from .conversion import from_bin, from_hex, decode, encode

# Universal networking constants.
all_interfaces = "0.0.0.0"
buffer_size = 4096
listen_bound = 5

# Custom types.
Operation_Result = Union[bytes, None]

def __safe_socket_operation(func: Callable, sock: socket, *args: tuple) -> Operation_Result:
    """
    Wrapper function to perform any socket operation.
    :params: func - Callable, sock - socket, args - tuple.
    :return: Result of the operation.
    """
    try:
        return func(sock, *args)
    except Exception as e:
        print(f"Error while: {func.__name__} on socket: {sock.getsockname()}, {e}")

def safe_recv(sock: socket) -> str:
    """
    Waits for data from sock.
    :params: sock - socket.
    :return: decoded data.
    """
    def nest_recv(sock: socket, buffer: int) -> bytes:
        return sock.recv(buffer)
    
    return decode(__safe_socket_operation(nest_recv, sock, buffer_size))

def safe_send(sock: socket, payload: str) -> None:
    """
    Sends a payload from sock.
    :params: sock - socket, payload - str.
    :return: None.
    """
    def nest_send(sock: socket, payload: str) -> bytes:
        return sock.send(encode(payload))
    
    __safe_socket_operation(nest_send, sock, payload)

def safe_send_recv(sock: socket, payload: str) -> str:
    """
    Sends a payload from sock and waits for an answer, using a safe operation.
    :params: sock - socket, payload - str.
    :return: Decoded answer.
    """
    safe_send(sock, payload)
    data = safe_recv(sock)
    return data
    
def create_new_thread(func: Callable, *args) -> Thread:
    """
    Creates a local thread.
    :params: func - Callable[[Client], None], args: list.
    :returns: Thread.
    """
    return Thread(target=func, args=args)
