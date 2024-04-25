import requests
from src.internal.system.transaction import Transaction

EXIT_NODES_API = "https://check.torproject.org/cgi-bin/TorBulkExitList.py"


def is_anonymous(tx: Transaction) -> bool:
    pass