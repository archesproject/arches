from importlib import import_module


def import_class_from_string(dotted_path):
    module_path, _, class_name = dotted_path.rpartition(".")
    mod = import_module(module_path)
    klass = getattr(mod, class_name)
    return klass
