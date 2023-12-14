
class SessionNotActive(Exception):
    """
    SessionNotActive indicates that an operation was called over an inactive session.
    """
    def __init__(self, info: str) -> None:
        super().__init__(info)
        
class WebServerNotRunning(Exception):    
    """
    WebServerNotRunning indicates that an connection was initiated over a closed machine.
    """
    def __init__(self, info: str) -> None:
        super().__init__(info)