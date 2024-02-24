import secrets
import collections
from string import digits, ascii_lowercase

TOKEN_LEN = 8
SEPERATOR = ';'
CHOICES = digits + ascii_lowercase

Rule = collections.namedtuple("Rule", "id description")

def tokenize() -> str:
    """Creates a token for each event."""
    return ''.join(
            secrets.choice(CHOICES) 
            for _ in range(TOKEN_LEN))
    
def parse_rule_string(r_str: str) -> Rule:
    ruid, desc = r_str.split(SEPERATOR)
    return Rule(ruid, desc) 