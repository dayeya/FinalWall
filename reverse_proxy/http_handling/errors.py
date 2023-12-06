
class SessionNotActive(Exception):
    """
    SessionNotActive indicates that an operation was called over an inactive session.
    """
    def __init__(self, info: str) -> None:
        super().__init__(info)