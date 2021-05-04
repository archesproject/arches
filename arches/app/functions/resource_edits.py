from arches.app.functions.base import BaseFunction
from django.utils.module_loading import import_string

class ResourceEdits(BaseFunction):
    def __init__(self, config=None, nodegroup_id=None):
        self.config = config
        self.nodegroup_id = nodegroup_id

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def save(self, tile, request):
        Func = import_string(self.config['modulename'])()
        Func.save(tile, request)

    # occurrs after Tile.save
    def post_save(self, *args, **kwargs):
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        raise NotImplementedError

    def on_import(self, *args, **kwargs):
        raise NotImplementedError

    # saves changes to the function itself
    def after_function_save(self, *args, **kwargs):
        raise NotImplementedError
