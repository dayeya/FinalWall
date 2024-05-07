import tomllib
from typing import Any
from pathlib import Path

ROOT_DIR = Path(__file__).parent
CONFIG_FILE = ROOT_DIR / "configuration.toml"


def _parse_toml() -> dict:
    """
    Parses the config file.
    :return: dict
    """
    try:
        with open(CONFIG_FILE, 'rb') as conf:
            configuration: dict[str, Any] = tomllib.load(conf)
            return configuration
    except FileNotFoundError as _file_err:
        raise _file_err


class WafConfig:
    """
    A class for accessing configurations about the Waf instance.
    """
    def __init__(self) -> None:
        self.reserve = {}
        config = _parse_toml()
        for field, value in config.items():
            setattr(self, field.lower(), value)
            self.reserve[field] = value

    def __getattr__(self, item):
        try:
            return self.reserve[item]
        except KeyError:
            print(f"ERROR: waf config has no field named {item}.")
