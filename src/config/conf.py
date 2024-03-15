import tomllib
from typing import Any
from pathlib import Path

ROOT_DIR = Path(__file__)
CONFIG_FILE = "config.toml"

def full_path(file: str) -> Path:
    return ROOT_DIR.parent.joinpath(file)
    
def load_config() -> dict:
    try:
        with open(full_path(CONFIG_FILE), 'rb') as conf:
            data = tomllib.load(conf)
            
        server = data.get('WebServer')
        proxy  = data.get('Proxy')
        admin  = data.get('Admin')
        
        return {
            "Server": (server["ip"], server["port"]),
            "Proxy": (proxy["ip"],  proxy["port"]),
            "Admin": (admin["ip"],  admin["port"])
        }
            
    except FileNotFoundError as file_error:
        # TODO: Handle this error.
        raise file_error

class Config:
    def __init__(self) -> None:
        self.conf = load_config()
        
    def __getitem__(self, __item: str) -> Any:
        return self.conf[__item]