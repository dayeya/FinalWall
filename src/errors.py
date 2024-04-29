class VersionError(Exception):
    """
    Raised when trying to run application.py with an unsupported python version.
    """
    pass


class StateError(Exception):
    """
    Raised when Waf.work() is called upon a closed or a working instance.
    """
    pass


class EntityShutdown(Exception):
    """
    Raised when an AsyncStream.write() or async for AsyncStream() fails due to the Host being down.
    """
    pass


class WebServerOffline(EntityShutdown):
    """
    Wrapper exception that raised when the target machine is not up.
    """
    pass


class AclFetchError(Exception):
    """
    Raised when Access List activity loop fails to fetch from API or backup sources.
    """
    pass


class AclBackUpError(Exception):
    """
    Raised when backup options for a fetching resource isn't available or not found.
    """
    pass


class AttackDetected(Exception):
    """
    Raised when a Waf detects an attack.
    """
    pass


# Warnings.


class EntityShutdownWarning(Warning):
    """
    Raised when an IO operation was called upon a closed connection or entity.
    """
    pass


class UnauthorizedClientFound(Warning):
    """
    Raised when a client was blocked and is now seeking their security page.
    Note:
        This warning is just for `jumping` reasons to handle sec page delivery.
    """
    def __init__(self, flags: int=0, token: str="", *args: tuple):
        super().__init__(*args)
        self.token = token
        self.flags = flags
