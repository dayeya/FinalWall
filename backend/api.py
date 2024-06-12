#
# FinalWall - A simple API for integration of the UI with the WAF engine.
# Author: Dayeya.
#

import asyncio
import pickle
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
import websockets.exceptions
from websockets.server import serve, WebSocketServerProtocol

from finalwall import JSONIZER
from finalwall.errors import VersionError
from finalwall.net import create_new_thread
from finalwall.time_utils import get_unix_time
from extensions.log_setup import create_logger


class FinalWallApi(Flask):
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

    @classmethod
    def process_event_data(cls, event_type: TunnelEvent, data):
        """Processes the data of the event in order to forward it to the Frontend."""
        if event_type == TunnelEvent.TunnelConnection:
            return get_unix_time("Asia/Jerusalem")
        elif event_type == TunnelEvent.AccessLogUpdate:
            return [JSONIZER(_event) for _event in data]
        elif event_type == TunnelEvent.SecurityLogUpdate:
            return {"events": [JSONIZER(_event) for _event in data["events"]], "distribution": data["distribution"]}
        return data

    async def tunnel_thread(self):
        """Starts the websocket tunnel server."""
        async def __tunnel_event_handler(websocket: WebSocketServerProtocol):
            """Handler for the catching events from the main cluster."""
            try:
                async for event in websocket:
                    async with asyncio.Lock():
                        event_type, data = pickle.loads(event)
                        processed_data = FinalWallApi.process_event_data(event_type, data)
                        self.__socketIO.emit(event_type, processed_data)

            except websockets.exceptions.ConnectionClosed:
                """Can either be raised from poor connectivity or large amounts of traffic."""
                return

        async with serve(__tunnel_event_handler, "localhost", 8765):
            await asyncio.get_event_loop().create_future()


async def main() -> None:
    """Main entry for the API."""
    app = FinalWallApi(import_name=__name__)
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
