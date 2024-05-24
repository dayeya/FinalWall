from engine import Waf, WafConfig, TunnelEvent
from engine.errors import VersionError, StateError
from engine.net import create_new_task, create_new_thread, looper

from backend.deps.ops import Operation
from backend.deps.fwlogs import create_logger

import asyncio
from flask_cors import CORS
from websockets.server import serve, WebSocketServerProtocol
from flask import Flask, jsonify, request


@looper
async def start_cluster(cluster: Waf) -> None:
    """
    Starts a cluster upon a request from the admin.
    This will be run in a separate thread of the backend server.
    """
    await cluster.deploy()
    work = [
        create_new_task(task_name=Operation.CLUSTER_WORK_LOOP, task=cluster.work, args=()),
        create_new_task(task_name=Operation.CLUSTER_ACL_LOOP, task=cluster.start_acl_loop, args=())
    ]
    await asyncio.gather(*work)


class FWServer(Flask):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.__server = None
        self.__total_clusters = 0
        self.__clusters: dict[int, Waf] = {}
        self.__logger = create_logger(name="FinalWallServer")

        self.__set_url_rules()
        self.__tunnel_thread = create_new_thread(func=asyncio.run, args=(self.__start_tunnel_server(), ), daemon=True)

        self.__logger.info("FWServer initiated.")

    def start_tunnel_server(self):
        """Starts the thread for the tunnel thread which will handle events coming from all clusters."""
        self.__tunnel_thread.start()

    async def __start_tunnel_server(self):
        """Starts the websocket tunnel server."""
        async with serve(self.__tunnel_event_handler, "localhost", 8765):
            await asyncio.get_event_loop().create_future()

    async def __tunnel_event_handler(self, websocket: WebSocketServerProtocol):
        """
        Handler that handles each event for each cluster.
        This handler is the main mechanism of real-time updates.
        """
        async for event in websocket:
            if event is TunnelEvent.AccessLogUpdate:
                print("A cluster has a access log update!")
            elif event is TunnelEvent.SecurityLogUpdate:
                print("A cluster hash a security log update!")
            else:
                print(f"Registered -> {event}")

    def __set_url_rules(self):
        """
        Sets the URL rules for every API endpoint.
        """
        self.add_url_rule("/events", view_func=self.events_handler, methods=["GET"])
        self.add_url_rule("/clusters", view_func=self.clusters_handler, methods=["GET", "POST"])

    def register_cluster(self) -> Waf:
        """
        Registers a FinalWall WAF cluster.
        Each cluster is given a unique id (The clusters index).
        """
        config = WafConfig()
        ucid = self.__total_clusters + 1
        cluster = Waf(ucid, config, with_tunneling=True)
        self.__clusters[ucid] = cluster
        self.__total_clusters += 1
        return cluster

    def cluster_report(self, ucid: int) -> dict:
        """Builds a report of a cluster with a given unique cluster id."""
        def format_address(host: tuple) -> str:
            return host[0] + ":" + str(host[1])

        cluster = self.__clusters[ucid]
        return {
            "ucid": ucid,
            "host": format_address(cluster.address),
            "endpoint": format_address(cluster.target),
            "status": cluster.state.name
        }

    def clusters_handler(self):
        """
        Handler of '/admin/clusters'.
        API GET request: Fetches a cluster report containing data related to all clusters.
        API POST request: Creates a new cluster and starts its thread.
        """
        if request.method == "GET":
            clusters_info = [self.cluster_report(ucid) for ucid in self.__clusters.keys()]
            return jsonify({"clusters": clusters_info})

        elif request.method == "POST":
            try:
                cluster = self.register_cluster()
                cluster_thread = create_new_thread(func=asyncio.run, args=(start_cluster(cluster),))
                cluster_thread.start()
                return jsonify({
                    "status": Operation.CLUSTER_REGISTRATION_SUCCESSFUL
                })
            except (StateError, OSError):
                return jsonify({
                    "status": Operation.CLUSTER_REGISTRATION_FAILURE
                })

    def events_handler(self):
        return jsonify({"Events": ["One"]})


if __name__ == "__main__":
    import tracemalloc
    tracemalloc.start()

    import sys

    if sys.version_info[0:2] != (3, 12):
        raise VersionError("Wrong python version. Please use +=3.12 only")

    app = FWServer(import_name=__name__)
    CORS(app, resources={r"*": {"origins": "*"}})

    app.start_tunnel_server()

    app.run(host="localhost", port=5001)
