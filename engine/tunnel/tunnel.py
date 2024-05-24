from enum import StrEnum
from engine.errors import StateError
from websockets.sync.client import (
    connect,
    ClientConnection as WebSocketConnection
)


class TunnelEvent(StrEnum):
    TunnelConnection = 'tunnel_connection'
    TunnelDisconnection = 'tunnel_disconnection'
    AccessLogUpdate = 'access_log_update'
    SecurityLogUpdate = 'security_log_update'


class Tunnel:
    """
    A tunnel for communicating with the admin backend server.
    This tunnel will notify the admin of every event of the Waf system.
    """
    def __init__(self, endpoint: str, auto_con=False):
        self.__tunnel_endpoint = endpoint
        self.__websocket: WebSocketConnection = connect(endpoint) if auto_con else None

    @property
    def endpoint(self) -> str:
        return self.__tunnel_endpoint

    def connect(self):
        """Connects to the endpoint."""
        self.__websocket = connect(self.__tunnel_endpoint)

    def reconnect(self):
        """Reconnects to the endpoint."""
        if self.__websocket is not None:
            raise StateError("Tunnel is open...")
        self.connect()

    def register_event(self, event: TunnelEvent):
        """Sends a tunnel event to the endpoint."""
        self.__websocket.send(event)
