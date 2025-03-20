class Singleton:
    """Base class for all singleton objects."""
    _instance = None

    def __new__(cls, *args, **kwds):
        """Ensuring there's only one instance of this object."""
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance
    
    def __init__(self):
        raise NotImplementedError
    
class PerArgumentSingleton:
    """Singleton class that allows multiple instances, each with unique argument(s)."""
    _instances = {}

    def __new__(cls, *args, **kwds):
        instance_key = tuple(list(args) + [val for val in kwds.values()])
        if instance_key not in cls._instances:
            cls._instances[instance_key] = object.__new__(cls)
        return cls._instances[instance_key]