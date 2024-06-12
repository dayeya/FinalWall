#
# FinalWall - Singleton pattern.
# Author: Dayeya.
#

from typing import Type

Inheritor = Type[object]


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(type(cls), cls).__call__(*args, **kwargs)
        return cls._instances[cls]
