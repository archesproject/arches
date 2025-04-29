from django.conf import settings

from arches.app.utils import import_class_from_string


def add_to_update_fields(kwargs, field_name):
    """
    Update the `update_field` arg inside `kwargs` (if present) in-place
    with `field_name`.
    """
    if (update_fields := kwargs.get("update_fields")) is not None:
        if isinstance(update_fields, set):
            # Django sends a set from update_or_create()
            update_fields.add(field_name)
        else:
            # Arches sends a list from tile POST view
            new = set(update_fields)
            new.add(field_name)
            kwargs["update_fields"] = new


def field_names(instance_or_class):
    return {f.name for f in instance_or_class._meta.fields}


def get_filename_generator_class():
    return import_class_from_string(settings.FILENAME_GENERATOR)
