class UnauthorizedClientFound(Exception):
    """
    Raised whenever a bad client is found from either anonymity and geolocation.
    """
    def __init__(self, flags: int, *args: tuple):
        super().__init__(*args)
        self.flags = flags
