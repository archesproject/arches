class BaseFunction(object):

    def __init__(self, config=None):
        self.config = config

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        raise NotImplementedError

    def on_import(self, *args, **kwargs):
        raise NotImplementedError
