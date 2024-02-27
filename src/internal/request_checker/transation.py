from dataclasses import dataclass
from typing import Optional

class Method:
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"
    TRACE = "TRACE"
    CONNECT = "CONNECT"
    OPTIONS = "OPTIONS"

class Parser:
    """
    Normalizes data encoded in different methods. 
    """
    
@dataclass(slots=True)
class Transaction:
    """
    Creates a signature of each HTTP request.
    """
    raw_tx: bytes
    token: Optional[str]
    id: str = ""
    method: Method = Method.GET
    
    def create_transaction_id(self) -> None:
        pass
    
    def process(self) -> None: 
        # TODO: Determine the context of the transaction.
        pass 
        
        
if __name__ == "__main__":
    pass