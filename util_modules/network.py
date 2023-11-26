"""
Network module.
Author Daniel Sapojnikov, 2023.
"""

# TODO - Remove some doc strings of functions that are not used.

import sys
from socket import *
from threading import Thread
from functools import partial
from network_client import Client
from typing import Callable

# Universal networking constants.
UNIVERSAL_IP = "0.0.0.0"
UNIVERSAL_BUFFER = 4096
UNIVERSAL_LISTEN_BOUND = 5

def convert(n: str, base: int=10) -> int:
    """
    Converts a number into integer based on specific base.
    
    Args:
        n - str: number of any base
        base -int: base of conversion. Defaults to decimal.
        
    Returns:
        int: Converted integer.
    """
    try:
        return int(n, base=base)
    except ValueError:
        raise ValueError(f"Invalid input for conversion of base {base}")

from_bin = partial(convert, base=2)
from_bin.__doc__ = 'Converts a base 2 into integer.'

from_hex = partial(convert, base=16)
from_hex.__doc__ = 'Converts a base 16 into integer.'

decode = partial(bytes.decode, encoding='utf-8')
decode.__doc__ = 'Decodes bytes using utf-8.'

encode = partial(str.encode, encoding='utf-8')
encode.__doc__ = 'Encodes bytes using utf-8.'

# Communication operations.

def recv(sock: socket) -> str:
    """
    Waits for a recv from sock.

    Args:
        sock - socket: Socket.

    Returns:
        str: Recieved decoded data.
    """
    try:
        return decode(sock.recv(UNIVERSAL_BUFFER))
    except Exception as e:
        print(f'[!] {e} Could not recieve any data from: {sock.getsockname()}')

def send(sock: socket, payload: str) -> None:
    """
    Sends a payload from a socket.

    Args:
        sock - socket: Socket.
        payload - str: Payload to send.
    """
    try:
        sock.send(encode(payload))
    except Exception as e:
        print(f'[!] {e} Could not send any data to: {sock.getpeername()}')

def send_recv(sock: socket, payload: str) -> str:
    """
    Sends a payload and returns its answer.

    Args:
        sock - socket: Socket.
        payload - str: Payload to send.

    Returns:
        str: Answer to a given payload.
    """
    send(sock, payload)
    data = recv(sock)
    return data
    
def create_thread(func: Callable[[Client], None], *args) -> Thread:
    """
    Creates a thread locally.
    
    Returns:
        Thread: A new thread.
    """
    return Thread(target=func, args=args)
