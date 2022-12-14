from arches.app.functions.base import BaseFunction
from django.utils.module_loading import import_string


class ResourceEdits(BaseFunction):
    def get(self, *args, **kwargs):
        Func = import_string(self.config["modulename"])()
        Func.get(self, *args, **kwargs)

    def save(self, *args, **kwargs):
        Func = import_string(self.config["modulename"])()
        Func.save(self, *args, **kwargs)

    def post_save(self, *args, **kwargs):
        Func = import_string(self.config["modulename"])()
        Func.post_save(self, *args, **kwargs)

    def delete(self, *args, **kwargs):
        Func = import_string(self.config["modulename"])()
        Func.delete(self, *args, **kwargs)

    def on_import(self, *args, **kwargs):
        Func = import_string(self.config["modulename"])()
        Func.on_import(self, *args, **kwargs)

    # saves changes to the function itself
    def after_function_save(self, *args, **kwargs):
        Func = import_string(self.config["modulename"])()
        Func.after_function_save(self, *args, **kwargs)
