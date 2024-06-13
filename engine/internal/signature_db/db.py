#
# FinalWall - A database handler for all the signatures.
# Author: Dayeya
#

import json
from enum import Enum
from pathlib import Path
from engine.singleton import Singleton

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
    path: Path = Path()
    try:
        path = abs_node_path(ROOT_FOLDER).joinpath(json_file)
        with open(path, "r") as json_data:
            return json.load(json_data)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"{json_file} not found at {path}. Double check the given file."
        )


class DbState(Enum):
    EMPTY = "Empty"
    LOADED = "Loaded"


class _BaseDb:
    _state: DbState = DbState.EMPTY

    def __init__(self) -> None:
        if _BaseDb._state is DbState.LOADED:
            return
        self.sql_data_set: dict = _load_json_file("sql_data.json")
        self.xss_data_set: dict = _load_json_file("xss_data.json")
        self.unauthorized_access_data_set: list = _load_unauthorized_data()
        _BaseDb._state = DbState.LOADED

    @classmethod
    def get_state(cls):
        return cls._state

    @classmethod
    def set_state(cls, state: DbState):
        if not isinstance(state, DbState):
            raise ValueError(
                f"Invalid argument type for {cls.set_state.__name__}. Expected DbState, got {type(state).__name__}."
            )
        cls._state = state


class SignatureDb(_BaseDb, metaclass=Singleton):
    """
    Singleton database object.
    """
    pass


__all__ = [
    "SignatureDb",
    "DbState"
]
