class VersionError(Exception):
    """
    Raised when trying to run application.py with an unsupported python version.
    """
    def __init__(self, *args):
        super().__init__(*args)


class StateError(Exception):
    """
    Raised when Waf.work() is called upon a closed or a working instance.
    """
    def __init__(self, *args):
        super().__init__(*args)


class EntityShutdown(Exception):
    """
    Raised when an AsyncStream.write() or async for AsyncStream() fails due to the Host being down.
    """
    def __init__(self, *args):
        super().__init__(*args)
