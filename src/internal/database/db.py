import json
from pathlib import Path
from typing import Generator

def abs_json_path(file_name: str, *nodes) -> Path:
    """Computes the absolute path of jname (based on this root dir)"""
    hpath_parent = Path(__file__).parent
    for n in nodes: 
        hpath_parent = hpath_parent.joinpath(n)
    full_path = hpath_parent.joinpath(file_name)
    return full_path

def load_rules() -> dict:
    """Loads all rules from db"""
    with open(abs_json_path('database/rules.json'), 'r') as r:
        return json.loads(r.read())

def load_signatures(source_file: str) -> Generator:
    try:
        source = abs_json_path(source_file, "signatures")
        is_signature = lambda s: s and not s.strip().startswith("#") 
        with open(source, "r") as f:
            data = set([line.strip() for line in f.readlines()])
            return set(filter(is_signature, data))
    except FileNotFoundError:
        # Empty set, for now.
        return set([])