from typing import Tuple, Union
from socket import socket, MSG_PEEK
from dataclasses import dataclass
from net.aionetwork import safe_recv, SafeRecv

type Address = Tuple[str, int]

@dataclass(slots=True)
class Connection:
    sock: socket
    host_addr: Address

    @property
    def address(self) -> Address:
        return self.host_addr

    def close(self) -> None:
        self.sock.close()

    def __hash__(self) -> int:
        return hash((self.sock, self.host_addr))

    async def recv(self) -> SafeRecv:
        data, err = await safe_recv(self.sock, buffer_size=8192)
        if not err:
            self.close()
        return data

class ClientConnection(Connection):
    def __init__(self, sock: socket, addr: Address) -> None:
        super().__init__(sock, addr)

    def __repr__(self) -> str:
        return (
            f"ClientConnection(peer={self.sock.getpeername()}, addr={self.host_addr})"
        )

class ServerConnection(Connection):
    def __init__(self, sock: socket, addr: Address) -> None:
        super().__init__(sock, addr)

    def __repr__(self) -> str:
        return (
            f"ServerConnection(peer={self.sock.getpeername()}, addr={self.host_addr})"
        )

type ConnectionType = Union[ClientConnection, ServerConnection]
type NetworkObject = Union[ConnectionType, socket]

def close_all(*objects: Tuple[NetworkObject]) -> None:
    for closable in objects:
        try:
            closable.close()
        except Exception as close_error:
            classify = closable.__class__.__name__
            print(f"[!] {classify}.close() was not complete. {close_error}")

def is_closed(object: NetworkObject) -> bool:
    try:
        obj_sock = object.sock if not isinstance(object, socket) else object
        return not bool(obj_sock.recv(1, MSG_PEEK))
    except:
        return True

def determine_conn(conn_type: ConnectionType) -> str:
    """returns the connection type as a string"""
    return repr(conn_type)[:6].lower()
