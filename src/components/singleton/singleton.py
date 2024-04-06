from typing import Type
from collections import defaultdict

Inheritor = Type[object]


class Singleton(object):
    _instance = defaultdict(object)

    def __new__(cls, *args, **kwargs):
        if not isinstance(Singleton._instance[cls], cls):
            Singleton._instance[cls] = super().__new__(cls, *args, **kwargs)
        return Singleton._instance[cls]
