import secrets
from string import digits, ascii_lowercase
# from src.internal.system.transaction import Transaction


TOKEN_LEN = 8
CHOICES = digits + ascii_lowercase


def tokenize() -> str:
    """
    Creates a token for each security event.
    :returns: Token.
    """
    shuffle_results = [secrets.choice(CHOICES) for _ in range(TOKEN_LEN)]
    return ''.join(shuffle_results)
