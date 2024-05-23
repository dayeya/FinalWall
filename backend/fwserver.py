from ops import Operation
from engine import Waf, WafConfig
from engine.errors import VersionError, StateError
from engine.net import create_new_task, create_new_thread, looper

import asyncio
from flask_cors import CORS
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

        self.__total_clusters = 0
        self.__clusters: list[Waf] = []

        self.__set_url_rules()

    def __set_url_rules(self):
        """
        Sets the URL rules for every API endpoint.
        """
        self.add_url_rule("/clusters", view_func=self.clusters_handler, methods=["GET", "POST"])

    def register_cluster(self) -> Waf:
        """
        Registers a FinalWall WAF cluster.
        Each cluster is given a unique id (The clusters index).
        """
        config = WafConfig()
        cluster = Waf(self.__total_clusters + 1, config)
        self.__clusters.append(cluster)
        self.__total_clusters += 1
        return cluster

    def clusters_handler(self):
        """
        This method is the handler of '/admin/clusters'.
        """
        if request.method == "GET":
            clusters_info = [{
                "ucid": cluster.ucid,
                "ip": cluster.address[0],
                "port": cluster.address[1],
                "endpoint": cluster.target[0] + ':' + str(cluster.target[1]),
                "status": cluster.state.name
            } for cluster in self.__clusters]
            return jsonify({"clusters": clusters_info})

        elif request.method == "POST":
            try:
                cluster = self.register_cluster()
                cluster_thread = create_new_thread(func=asyncio.run, args=(start_cluster(cluster),))
                cluster_thread.start()
                return {"status": Operation.CLUSTER_REGISTRATION_SUCCESSFUL}
            except (StateError, OSError):
                return {"status": Operation.CLUSTER_REGISTRATION_FAILURE}


if __name__ == "__main__":
    import tracemalloc
    tracemalloc.start()

    import sys

    if sys.version_info[0:2] != (3, 12):
        raise VersionError("Wrong python version. Please use +=3.12 only")

    app = FWServer(import_name=__name__)
    CORS(app, resources={r"*": {"origins": "*"}})

    app.run(host="localhost", port=5001)
