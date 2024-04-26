import json
from enum import Enum
from pathlib import Path
from src.components import Singleton

ROOT_FOLDER = "signatures"


def abs_node_path(node: str, *other_nodes) -> Path:
    """
    Computes the absolute path of node (based on this root dir) joining each given node.
    :returns: absolute path
    """
    this_root = Path(__file__).parent
    for n in other_nodes: 
        this_root = this_root.joinpath(n)
    absolute_path = this_root.joinpath(node)
    return absolute_path


def _load_unauthorized_data() -> list:
    def _filter_data(_data: str) -> bool:
        return not _data.startswith("#") and _data

    path = abs_node_path(ROOT_FOLDER).joinpath("unauthorized_access.txt")
    with open(path, "r") as unauthorized_locations:
        return list(filter(_filter_data, unauthorized_locations.read().splitlines()))


def _load_json_file(json_file: str) -> dict:
    # TODO: Handle exceptions.
    try:
        path = abs_node_path(ROOT_FOLDER).joinpath(json_file)
        with open(path, "r") as json_data:
            return json.load(json_data)
    except Exception as _e:
        raise _e


class _DbState(Enum):
    EMPTY = "Empty"
    LOADED = "Loaded"


class SignaturesDB(Singleton):
    state: _DbState = _DbState.EMPTY

    def __init__(self) -> None:
        if not SignaturesDB.state == _DbState.LOADED:
            self.sql_data_set: dict = _load_json_file("sql_data.json")
            self.xss_data_set: dict = _load_json_file("xss_data.json")
            self.unauthorized_access_data_set: list = _load_unauthorized_data()


SIGNATURE_DB = SignaturesDB()
SignaturesDB.state = _DbState.LOADED

__all__ = ["SIGNATURE_DB"]
