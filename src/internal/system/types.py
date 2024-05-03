from typing import Callable
from dataclasses import dataclass

from .logging import AttackClassifier

# Constants to differ the
ANONYMOUS = 0x00000002
GEOLOCATION = 0x00000004


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
    classifiers: list[AttackClassifier]
