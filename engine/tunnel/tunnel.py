#
# FinalWall - Tunnel architecture.
# Author: Dayeya.
#

import asyncio
import pickle
from enum import StrEnum
import websockets.exceptions

from engine.errors import StateError
from websockets.sync.client import connect

type EventResult = str | bytes


class TunnelEvent(StrEnum):
    TunnelConnection = 'tunnel_connection'
    TunnelDisconnection = 'tunnel_disconnection'

    AccessLogUpdate = 'access_log_update'
    SecurityLogUpdate = 'security_log_update'

    AttackDistributionUpdate = 'attack_distribution_update'
    WafHealthUpdate = 'waf_health_update'
    WafServicesUpdate = 'waf_services_update'


class Tunnel:
    """
    A tunnel for communicating with the admin backend server.
    This tunnel will notify the admin of every event of the Waf system.
    """
    def __init__(self, endpoint: str):
        self.__connected = False
        self.__websocket = None
        self.__event_queue = asyncio.Queue()
        self.__tunnel_endpoint = endpoint

    @property
    def endpoint(self) -> str:
        return self.__tunnel_endpoint

    @property
    def connected(self) -> bool:
        return self.__connected

    async def connect(self, timeout=10):
        """
        Connects to the endpoint.
        Executes all events that were published in the connection process.
        It does that by saving them in a queue and registers them one by one in order.
        """
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
            self.__connected = True
            await self.register_event(pickle.dumps((TunnelEvent.TunnelConnection, '')))
            while not self.__event_queue.empty():
                await self.register_event(await self.__event_queue.get())
            print(f"Tunnel is connected to {self.__tunnel_endpoint}")
        except asyncio.TimeoutError:
            print("Timeout for tunnel connection has ended.")
            return

    async def reconnect(self):
        """Reconnects to the endpoint."""
        if self.__websocket is not None or not self.__connected:
            raise StateError("Tunnel is open.")
        await self.connect()

    async def register_event(self, event: bytes):
        """Sends a tunnel event to the endpoint."""
        try:
            if not self.connected:
                await self.__event_queue.put(event)
                return
            self.__websocket.send(event)
        except websockets.exceptions.ConnectionClosedError:
            """Tunnel is closed."""
            return

    def recv_result(self) -> EventResult:
        """Returns the data sent from the websocket server."""
        return self.__websocket.recv()

    def register_recv(self, event) -> EventResult:
        """Performs a send/recv operation."""
        self.register_event(event)
        return self.recv_result()
