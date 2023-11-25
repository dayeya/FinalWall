"""
Network module.
Author Daniel Sapojnikov, 2023.
"""
import sys
import socket
from functools import partial

def convert(n: str, base: int=10) -> int:
    """
    Converts a number into integer based on specific base.
    
    Args:
        n - str: number of any base
        base -int: base of conversion. Defaults to decimal.
        
    Returns:
        int: Converted integer.
    """
    try:
        return int(n, base=base)
    except ValueError:
        raise ValueError(f"Invalid input for conversion of base {base}")

from_bin = partial(convert, base=2)
from_hex = partial(convert, base=16)