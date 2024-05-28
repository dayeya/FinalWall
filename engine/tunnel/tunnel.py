import asyncio
from enum import StrEnum

import websockets.exceptions

from engine.errors import StateError
from websockets.sync.client import (
    connect,
    ClientConnection as WebSocketConnection
)


class TunnelEvent(StrEnum):
    TunnelConnection = 'tunnel_connection'
    TunnelDisconnection = 'tunnel_disconnection'

    ClusterUpdate = 'cluster_update'
    ClusterLogUpdate = 'cluster_log_update'

    AccessLogUpdate = 'access_log_update'
    SecurityLogUpdate = 'security_log_update'

    vulnerabilityScoresUpdate = 'vulnerability_scores_update'
    packetFlowUpdate = 'packet_flow_update'


class Tunnel:
    """
    A tunnel for communicating with the admin backend server.
    This tunnel will notify the admin of every event of the Waf system.
    """
    def __init__(self, endpoint: str):
        self.__connected = False
        self.__websocket = None
        self.__tunnel_endpoint = endpoint

    @property
    def endpoint(self) -> str:
        return self.__tunnel_endpoint

    @property
    def connected(self) -> bool:
        return self.__connected

    async def connect(self, timeout=10):
        """Connects to the endpoint."""
        async def _connect():
            while True:
                try:
                    return connect(self.__tunnel_endpoint)
                except websockets.exceptions.InvalidHandshake:
                    break
                except ConnectionRefusedError:
                    """Server is not up so the tunnel waits for him."""
                    await asyncio.sleep(0.5)
        try:
            self.__websocket = await asyncio.wait_for(asyncio.create_task(_connect()), timeout=timeout)
            self.register_event(TunnelEvent.TunnelConnection)
            self.__connected = True
            print(f"Tunnel is connected to {self.__tunnel_endpoint}")
        except asyncio.TimeoutError:
            print("Timeout for tunnel connection has ended.")
            return

    async def reconnect(self):
        """Reconnects to the endpoint."""
        if self.__websocket is not None or not self.__connected:
            raise StateError("Tunnel is open.")
        await self.connect()

    def register_event(self, event: TunnelEvent):
        """Sends a tunnel event to the endpoint."""
        self.__websocket.send(event)

    def recv_publish(self) -> str | bytes:
        """Returns the data sent from the websocket server."""
        return self.__websocket.recv()
