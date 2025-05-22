import os
from pathlib import Path


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


def make_name_unique(name, names_to_check, suffix_delimiter="_"):
    """
    Makes a name unique among a list of names

    Arguments:
    name -- the name to check and modify to make unique in the list of "names_to_check"
    names_to_check -- a list of names that "name" should be unique among
    """

    i = 1
    temp_name = name
    while temp_name in names_to_check:
        temp_name = "{0}{1}{2}".format(name, suffix_delimiter, i)
        i += 1
    return temp_name


def format_file_into_sql(file: str, sql_dir: str):
    sql_file = Path(__file__).parent / sql_dir / file
    sql_string = ""
    with open(sql_file) as file:
        sql_string = sql_string + "\n" + file.read()
    return sql_string
