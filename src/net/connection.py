from typing import Tuple, Union
from socket import socket, MSG_PEEK
from dataclasses import dataclass
from net.aionetwork import safe_send, safe_recv, Safe_Recv_Result

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

    async def recv(self) -> Safe_Recv_Result:
        data, err = await safe_recv(self.sock, buffer_size=8192)
        if err:
            self.close()
        return data
    
    async def send(self, data: bytes) -> None:
        await safe_send(self.sock, data)

def close_all(*objects: Tuple[Connection]) -> None:
    for closable in objects:
        try:
            closable.close()
        except Exception as close_error:
            classify = closable.__class__.__name__
            print(f"[!] {classify}.close() was not complete. {close_error}")

def is_closed(object: Connection) -> bool:
    try:
        obj_sock = object.sock if not isinstance(object, socket) else object
        return not bool(obj_sock.recv(1, MSG_PEEK))
    except:
        return True
