import secrets
from string import digits, ascii_lowercase


TOKEN_LEN = 8
CHOICES = digits + ascii_lowercase


def tokenize() -> str:
    """Creates a token for each event."""
    return ''.join(
            secrets.choice(CHOICES) 
            for _ in range(TOKEN_LEN))