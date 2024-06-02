import json
import pickle
import websockets.exceptions

from engine import Tunnel, TunnelEvent
from engine.errors import VersionError
from engine.internal.events import Event
from engine.net import create_new_thread
from engine.time_utils import get_unix_time
from engine.internal.jsonable import ToJson

from backend.deps.ops import Operation
from backend.deps.fwlogs import create_logger

import asyncio
from flask_cors import CORS
from flask import Flask, jsonify
from flask_socketio import SocketIO
from websockets.server import serve, WebSocketServerProtocol


JSONIZER = ToJson()


class FWServer(Flask):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.__logger = create_logger(name="API")
        self.__socketIO = SocketIO(self, cors_allowed_origins="*", logger=False, engineio_logger=False)

        self.__logger.info("FinalWall API started.")

    def start_tunnel_server(self):
        """Starts tunnel listener."""
        asyncio.run(self.tunnel_thread())

    def start_tunnel_thread(self):
        """Starts the tunnel receiving thread."""
        create_new_thread(func=self.start_tunnel_server, args=(), daemon=True).start()

    async def tunnel_thread(self):
        """Starts the websocket tunnel server."""
        async def __tunnel_event_handler(websocket: WebSocketServerProtocol):
            """Handler for the catching events from the main cluster."""
            try:
                async for event in websocket:
                    async with asyncio.Lock():
                        event_type, data = pickle.loads(event)
                        if event_type == TunnelEvent.TunnelConnection:
                            data = get_unix_time("Asia/Jerusalem")
                        elif event_type == TunnelEvent.AccessLogUpdate:
                            data = [JSONIZER(_event) for _event in data]
                        elif event_type == TunnelEvent.SecurityLogUpdate:
                            data = {
                                "events": [JSONIZER(_event) for _event in data["events"]],
                                "distribution": data["distribution"]
                            }
                        print(f"Registered an event -> {event_type}")
                        self.__socketIO.emit(event_type, data)

            except websockets.exceptions.ConnectionClosed:
                """Can either be raised from poor connectivity or large amounts of traffic."""
                return

        async with serve(__tunnel_event_handler, "localhost", 8765):
            await asyncio.get_event_loop().create_future()


async def main():
    """Main entry for the API."""
    app = FWServer(import_name=__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.start_tunnel_thread()

    app.run(host="localhost", port=5001)


if __name__ == "__main__":
    import tracemalloc
    tracemalloc.start()

    import sys

    if sys.version_info[0:2] != (3, 12):
        raise VersionError("Wrong python version. Please use +=3.12 only")

    asyncio.run(main())
