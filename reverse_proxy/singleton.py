from typing import Type

Inheritor = Type[object]

class Singleton(type):
    __instances = {}
    
    def __call__(cls, *args, **kwargs) -> Inheritor:
        """
        Returns the instances if it exists, otherwise creates it.

        Returns:
            _type_: cls instance.
        """
        if cls not in cls.__instances:
            cls.__instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.__instances[cls]
