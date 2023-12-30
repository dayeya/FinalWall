import json
from pathlib import Path

def abs_json_path(file_name: str) -> Path:
    """Computes the absolute path of jname (based on this root dir)"""
    hpath_parent = Path(__file__).parent
    return hpath_parent.joinpath(file_name)

def load_rules() -> dict:
    """Loads all rules from db"""
    with open(abs_json_path('db/rules.json'), 'r') as r:
        return json.loads(r.read())
    
def format_rule(descriptor: dict) -> None:
    print(f"Number: {descriptor['num']}\n"
          f"Description: {descriptor['desc']}\n"
          f"Regex: {descriptor['patterns']}\n"
          f"{'-' * 30}")