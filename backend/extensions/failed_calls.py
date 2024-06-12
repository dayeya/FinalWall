#
# FinalWall - A class for wrapping a *failed* operation from constants.py
# Author: Dayeya.
#

import traceback


class FailedCall:
    def __init__(self, origin_code: int, cause: str, tb: traceback.TracebackException):
        self.__code = ~origin_code
        self.__cause = cause
        self.__tb = tb

    def __repr__(self):
        """Builds a string representation of Self."""
        return f"FailedCall(origin_code={self.__code}, cause={self.__cause}, traceback={self.__tb.format()})"