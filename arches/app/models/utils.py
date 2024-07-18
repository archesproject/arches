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


def field_names(instance):
    return {f.name for f in instance._meta.fields}
