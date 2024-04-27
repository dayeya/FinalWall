from typing import Callable
from dataclasses import dataclass

from .logging import LogType


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
    A class representing a result of the Checker.
    :result: Indicates if the transaction is malicious and should be blocked.
    :log: The log object produced by the Checker.
    """
    result: bool
    log: LogType | None

    def unwrap(self):
        return self.result

    def unwrap_log(self):
        return self.log
