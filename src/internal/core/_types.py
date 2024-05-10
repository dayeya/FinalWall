from typing import Callable
from dataclasses import dataclass

from ..events.classifier import Classifier


SQL_INJECTION = 1
XSS = 2
LFI = 3
RFI = 4
BRUTEFORCE = 5
UNAUTHORIZED_ACCESS = 6
ANONYMOUS = 7
GEOLOCATION = 8


@dataclass(slots=True)
class Check:
    """
    A class representing a check to be done.
    """
    fn: Callable
    args: tuple


@dataclass(slots=True)
class CheckResult:
    """
    A class representing a result of a check.

    Attributes
    ----------
    result - boolean indicating if the check passed or not.
    classifiers - If an attack is detected, the check function will return the classifier of the attack.
    """
    result: bool
    classifiers: list[Classifier]
