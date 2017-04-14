class BaseFunction(object):

    def __init__(self, config=None, nodegroup_id=None):
        self.config = config
        self.nodegroup_id = nodegroup_id

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        raise NotImplementedError

    def on_import(self, *args, **kwargs):
        raise NotImplementedError

    def after_function_save(self, *args, **kwargs):
        raise NotImplementedError
