import re
from typing import Tuple, Optional

def path_segment(payload: str) -> Tuple[Optional[str]]:
    for header in payload.split('\r\n'):
        match = re.search(r'\b(GET|POST|PUT|DELETE)\s+(/\S*)', header)
        if match:
            return match.groups()