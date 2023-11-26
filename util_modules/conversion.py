"""
Author: Daniel Sapojnikov, 2023.
Conversion module, contains useful conversion methods.
"""
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

# Base conversion partial functions.
from_bin = partial(convert, base=2)
from_bin.__doc__ = 'Converts a base 2 into integer.'

from_hex = partial(convert, base=16)
from_hex.__doc__ = 'Converts a base 16 into integer.'

# Encapsulation conversion partial functions.
decode = partial(bytes.decode, encoding='utf-8')
decode.__doc__ = 'Decodes bytes using utf-8.'

encode = partial(str.encode, encoding='utf-8')
encode.__doc__ = 'Encodes bytes using utf-8.'