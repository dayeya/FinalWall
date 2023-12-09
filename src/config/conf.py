import tomllib
from pathlib import Path

ROOT_DIR = Path(__file__)

def full_path(file: str) -> Path:
    return ROOT_DIR.parent.joinpath(file)
    
def load_config(toml_file: str) -> dict:
    try:
        with open(full_path(toml_file), 'rb') as conf:
            data = tomllib.load(conf)
            
        server = data.get('WebServer')
        proxy  = data.get('Proxy')
        admin  = data.get('Admin')
        
        return (
            (server["ip"], server["port"]),
            (proxy["ip"],  proxy["port"]),
            (admin["ip"],  admin["port"])
        )
            
    except FileNotFoundError as file_error:
        print(f'[!] {file_error} doesnt exist!')
