class AnonymousClient(Exception):
    """
    Raised when a Waf detects a client that identifies with a TOR exit node.
    """
    pass


class BadGeoLocation(Exception):
    """
    Raised when a Waf detects a client from an untrusted geolocation.
    """
    pass