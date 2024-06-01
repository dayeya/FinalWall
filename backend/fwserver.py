import pickle

import websockets.exceptions

from engine import Tunnel, TunnelEvent
from engine.errors import VersionError
from engine.internal.events import Event
from engine.net import create_new_thread

from backend.deps.ops import Operation
from backend.deps.fwlogs import create_logger

import asyncio
from flask_cors import CORS
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from websockets.server import serve, WebSocketServerProtocol


class FWServer(Flask):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.__cluster_ws = None
        self.__logger = create_logger(name="API")
        self.__tunnel = Tunnel("ws://localhost:8790")
        self.__socketIO = SocketIO(self, cors_allowed_origins="*", logger=False, engineio_logger=False)

        self.__logger.info("FinalWall API started.")

    def start_tunnel_server(self):
        """Starts tunnel listener."""
        asyncio.run(self.tunnel_thread())

    def connect_to_cluster_api(self):
        """Connects to the API of the cluster."""
        create_new_thread(func=asyncio.run, args=(self.__tunnel.connect(),)).start()

    def start_tunnel_thread(self):
        """Starts the tunnel receiving thread."""
        create_new_thread(func=self.start_tunnel_server, args=(), daemon=True).start()

    def set_rules(self):
        """Sets the URL rules for every API endpoint."""
        self.add_url_rule("/api/authorized_events", view_func=self.authorized_events_handler, methods=["GET"])
        self.add_url_rule("/api/security_events", view_func=self.security_events_handler, methods=["GET"])
        self.add_url_rule("/api/attack_distribution", view_func=self.attack_distribution, methods=["GET"])
        self.add_url_rule("/api/health", view_func=self.health, methods=["GET"])

    async def tunnel_thread(self):
        """Starts the websocket tunnel server."""
        async def __tunnel_event_handler(websocket: WebSocketServerProtocol):
            """Handler for the catching events from the main cluster."""
            try:
                async for event in websocket:
                    async with asyncio.Lock():
                        print(f"Registered an event -> {event}")
                        if event == TunnelEvent.AccessLogUpdate:
                            self.__socketIO.emit(TunnelEvent.AccessLogUpdate)
                        if event == TunnelEvent.SecurityLogUpdate:
                            self.__socketIO.emit(TunnelEvent.SecurityLogUpdate)
                        if event == TunnelEvent.AttackDistributionUpdate:
                            self.__socketIO.emit(TunnelEvent.AttackDistributionUpdate)
                        if event == TunnelEvent.WafHealthUpdate:
                            self.__socketIO.emit(TunnelEvent.WafHealthUpdate)

            except websockets.exceptions.ConnectionClosed:
                """Can either be raised from poor connectivity or large amounts of traffic."""
                return

        async with serve(__tunnel_event_handler, "localhost", 8765):
            await asyncio.get_event_loop().create_future()

    def authorized_events_handler(self):
        """Returns the authorized events to the frontend."""
        if not self.__tunnel.connected:
            return jsonify({
                "status": Operation.TUNNEL_CLOSED
            })
        pickled_events: bytes = self.__tunnel.register_recv(TunnelEvent.AccessLogUpdate)
        authorized_events: list[Event] = pickle.loads(pickled_events)

        # Format the events for API response.
        jsoned_events = [{
            "ip": event.log.ip,
            "id": event.id,
            "port": event.log.port,
            "date": event.log.creation_date,
            "url": event.request.url.path,
            "size": event.request.size,
            "geolocation": repr(event.log.geolocation),
            "downloadable": event.log.download
        } for event in authorized_events]

        return jsonify({
            "status": Operation.CLUSTER_EVENT_FETCHING_SUCCESSFUL,
            "events": jsoned_events
        })

    def security_events_handler(self):
        """Returns the security events to the frontend."""
        if not self.__tunnel.connected:
            return jsonify({
                "status": Operation.TUNNEL_CLOSED
            })
        pickled_events: bytes = self.__tunnel.register_recv(TunnelEvent.SecurityLogUpdate)
        security_events: list[Event] = pickle.loads(pickled_events)

        # Format the events for API response.
        jsoned_events = [{
            "activity_token": event.id,
            "date": event.log.creation_date,
            "ip": event.log.ip,
            "port": event.log.port,
            "classifiers": event.log.classifiers,
            "size": event.request.size,
            "geolocation": repr(event.log.geolocation),
            "downloadable": event.log.download
        } for event in security_events]

        return jsonify({
            "status": Operation.CLUSTER_EVENT_FETCHING_SUCCESSFUL,
            "events": jsoned_events
        })

    def attack_distribution(self):
        """Returns the vulnerability scores to the frontend."""
        if not self.__tunnel.connected:
            return jsonify({
                "status": Operation.TUNNEL_CLOSED
            })
        pickled_distributions: bytes = self.__tunnel.register_recv(TunnelEvent.AttackDistributionUpdate)
        attack_distributions: dict = pickle.loads(pickled_distributions)

        return jsonify({
            "status": Operation.CLUSTER_EVENT_FETCHING_SUCCESSFUL,
            "scores": attack_distributions
        })

    def health(self):
        """Returns the health of the Waf."""
        if not self.__tunnel.connected:
            return jsonify({
                "status": Operation.TUNNEL_CLOSED
            })
        pickled_health: bytes = self.__tunnel.register_recv(TunnelEvent.WafHealthUpdate)
        health: float = pickle.loads(pickled_health)
        return jsonify({
            "status": Operation.CLUSTER_HEALTH_SUCCESSFUL,
            "health": health
        })


async def main():
    """Main entry for the API."""
    app = FWServer(import_name=__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    app.set_rules()
    app.start_tunnel_thread()
    app.connect_to_cluster_api()

    app.run(host="localhost", port=5001)

if __name__ == "__main__":
    import tracemalloc
    tracemalloc.start()

    import sys

    if sys.version_info[0:2] != (3, 12):
        raise VersionError("Wrong python version. Please use +=3.12 only")

    asyncio.run(main())
