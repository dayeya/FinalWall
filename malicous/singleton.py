class Singleton(type):
    __instances = {}
    
    # function to fetch the singleton object.
    def __call__(cls, *args, **kwargs):
        """
        Returns the instances if it exists, otherwise creates it.

        Returns:
            _type_: cls instance.
        """
        if cls not in cls.__instances:
            cls.__instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.__instances[cls]