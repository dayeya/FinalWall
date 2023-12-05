"""
Author: Daniel Sapojnikov, 2023.
Network module contains useful function related to networking.
"""

from socket import socket
from typing import Tuple, Callable, Union
from threading import Thread
from .conversion import decode, encode

# Universal networking constants.
null_ip = "0.0.0.0"
loop_back = '127.0.0.1'
Address = Tuple[str, int]

# Custom types.
__recv_result = Tuple[bytes, int]
__send_result = int
SafeRecv = Tuple[bytes, int]
SafeSend = int
FunctionResult = Union[SafeRecv, SafeSend]

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

def safe_recv(sock: socket, buffer_size: int) -> SafeRecv:
    """
    Waits for data from sock.
    :params: sock, buffer_size.
    :return: decoded data.
    """
    def __recv(sock: socket, buffer: int) -> __recv_result:
        try:
            data = sock.recv(buffer)
        except:
            return b"", 0
            
        if len(data) == buffer:
            while True:
                try:
                    data += sock.recv(buffer)
                except:
                    break
        return data, 1

    return __safe_socket_operation(__recv, sock, buffer_size)

def safe_send(sock: socket, payload: bytes) -> None:
    """
    Sends a payload from sock.
    :params: sock, payload.
    :return: None.
    """
    def __send(sock: socket, payload: bytes) -> __send_result:
        return sock.send(payload)
        
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