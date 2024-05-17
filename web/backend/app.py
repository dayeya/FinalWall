from flask import Flask, Response, jsonify
from flask_cors import CORS


class Application(Flask):
    def __init__(self, waf_clusters: list[int], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__waf_clusters = waf_clusters
        self.__cors = None
        self.enable_cors()

    def enable_cors(self) -> None:
        # TODO: get resources from any clusters configuration.
        self.__cors = CORS(self, resources={r"/ping": {"origins": "*"}})

    @staticmethod
    def ping() -> Response:
        return jsonify("Pong!")


if __name__ == "__main__":
    waf_c0 = 0
    clusters = [waf_c0]

    app = Application(waf_clusters=clusters, import_name=__name__)
    app.add_url_rule("/ping", view_func=app.ping)

    app.run(host="localhost", port=5001)