from typing import Callable
from dataclasses import dataclass

from ..events.classifier import Classifier


SQL_INJECTION = 1
XSS = 2
FILE_INCLUSION = 3
BRUTEFORCE = 4
UNAUTHORIZED_ACCESS = 5
ANONYMOUS = 6
GEOLOCATION = 7


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
