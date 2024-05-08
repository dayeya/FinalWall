from enum import StrEnum


class Classifier(StrEnum):
    """
    Classifier is a part of the classification process of each Security Log. It tells the Waf why the event was triggered.
    Additionally, a classifier is the vulnerability identifier and the rationale behind the BLOCK action.

    Enum variants
    -------------
    Sql Injection - The transaction showed signs of SQL signatures.
    XSS - The transaction showed signs of XSS signatures.
    Unauthorized Access - The transactions `request-URI` or namely tx.url aims to access a forbidden location.
    Banned Access - The transaction was made by an already banned client.
    Banned Geolocation - The transaction was made by a client living in a banned geolocation.
    Anonymity - The transactions owner identifies with a banned software such as TOR.
    """
    SqlInjection = "Sql Injection"
    UnauthorizedAccess = "Unauthorized Access"
    BannedAccess = "Banned"
    BannedGeolocation = "Banned Geolocation"
    Anonymity = "Anonymization"


__all__ = [
    "Classifier"
]
