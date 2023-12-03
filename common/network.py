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
SafeRecv = str
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

def safe_recv(sock: socket, buffer_size: int) -> str:
    """
    Waits for data from sock.
    :params: sock, buffer_size.
    :return: decoded data.
    """
    __recv_result = Tuple[bytes, int]
    def __recv(sock: socket, buffer: int) -> __recv_result:
        """
        Basic recv function.
        """
        data = sock.recv()
        if not data:
            return b"", 0
            
        if len(data) == buffer:
            while True:
                try:
                    data += sock.recv(buffer)
                except:
                    break
                
        return data, 1
    
    return decode(__safe_socket_operation(__recv, sock, buffer_size))

def safe_send(sock: socket, payload: str) -> None:
    """
    Sends a payload from sock.
    :params: sock, payload.
    :return: None.
    """
    __send_result = int
    def __send(sock: socket, payload: str) -> __send_result:
        return sock.send(encode(payload))
    
    return __safe_socket_operation(__send, sock, payload)

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