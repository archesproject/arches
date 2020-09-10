class Singleton(type):
    '''
    A metaclass that ensures a subclass can only have a single instance
    '''
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            import pdb; pdb.set_trace()
        return cls._instances[cls]
