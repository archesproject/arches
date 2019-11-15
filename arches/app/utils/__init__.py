from importlib import import_module


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [dict(list(zip([col[0] for col in desc], row))) for row in cursor.fetchall()]


def import_class_from_string(dotted_path):
    module_path, _, class_name = dotted_path.rpartition(".")
    mod = import_module(module_path)
    klass = getattr(mod, class_name)
    return klass
