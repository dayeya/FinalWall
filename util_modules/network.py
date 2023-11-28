"""
Author: Daniel Sapojnikov, 2023.
Network module contains useful function related to networking.

Short function should be documented like this.
"""

import sys
from socket import *
from typing import Callable
from threading import Thread
from network_client import Client
from conversion import from_bin, from_hex, decode, encode

# Universal networking constants.
all_interfaces = "0.0.0.0"
buffer_size = 4096
listen_bound = 5

def recv(sock: socket) -> str:
    """
    Waits for data from sock.
    :params: sock - socket.
    :return: decoded data.
    """
    try:
        return decode(sock.recv(buffer_size))
    except Exception as e:
        print(f'[!] {e} Could not recieve any data from: {sock.getsockname()}')

def send(sock: socket, payload: str) -> None:
    """
    Sends a payload from sock.
    :params: sock - socket, payload - str.
    :return: None.
    """
    try:
        sock.send(encode(payload))
    except Exception as e:
        print(f'[!] {e} Could not send any data to: {sock.getpeername()}')

def send_recv(sock: socket, payload: str) -> str:
    """
    Sends a payload from sock and waits for an answer.
    :params: sock - socket, payload - str.
    :return: Decoded answer.
    """
    send(sock, payload)
    data = recv(sock)
    return data
    
def create_new_thread(func: Callable[[Client], None], *args) -> Thread:
    """
    Creates a local thread.
    :params: func - Callable[[Client], None], args: list.
    :returns: Thread.
    """
    return Thread(target=func, args=args)
