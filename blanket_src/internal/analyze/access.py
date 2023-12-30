import os
import re
import sys

DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.join(DIR, "../..")
sys.path.append(os.path.abspath(ROOT_DIR))
sys.path.append(os.path.abspath(os.path.join(DIR, "../...")))

from database import db
from http_tools import path_segment

def check_match(s: str, pattern: str) -> re.Match:
    return re.match(pattern, s)

def check_forbidden_path(path: str) -> bool:
    """
    This function will check for forbidden paths.
    """
    rdict = db.load_rules()
    for r in rdict:
        for p in r['patterns']:
            if check_match(path, p):
                return True
    return False

def contains_forbidden_words(packet: bytes) -> bool:
    """Determines if the packet contains forbidden paths."""
    _method, path = path_segment(str(packet))
    if check_forbidden_path(path):
        return True
    return False