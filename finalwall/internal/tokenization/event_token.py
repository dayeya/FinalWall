#
# FinalWall - A tokenizer for Security Events.
# Author: Dayeya
#

import secrets
from string import digits, ascii_lowercase


TOKEN_LEN = 8
CHOICES = digits + ascii_lowercase


def tokenize() -> str:
    """
    Creates a token for each security event.
    :returns: Token.
    """
    shuffle_results = [secrets.choice(CHOICES) for _ in range(TOKEN_LEN)]
    return ''.join(shuffle_results)
