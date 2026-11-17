from pathlib import Path

from django.db import connection


def add_to_update_fields(kwargs, field_name):
    """Return new kwargs with any `update_field` kwarg augmented with `field_name`."""
    if update_fields := kwargs.get("update_fields"):
        return {
            **kwargs,
            "update_fields": {*update_fields, field_name},
        }
    return kwargs


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


def get_slugified_alias_renames(aliases_by_nodeid):
    """
    Returns a new alias, keyed by nodeid, for each alias in a single graph that
    is not already a valid slug. New aliases remain unique within the graph.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "select alias, __arches_slugify(alias) from unnest(%s::text[]) as alias",
            [list(set(aliases_by_nodeid.values()))],
        )
        slugified_aliases = dict(cursor.fetchall())

    nodeids_to_rename = {
        nodeid
        for nodeid, alias in aliases_by_nodeid.items()
        if slugified_aliases[alias] != alias
    }
    reserved_aliases = {
        alias
        for nodeid, alias in aliases_by_nodeid.items()
        if nodeid not in nodeids_to_rename
    }

    new_aliases_by_nodeid = {}
    for nodeid in sorted(
        nodeids_to_rename,
        key=lambda nodeid: (aliases_by_nodeid[nodeid], str(nodeid)),
    ):
        new_alias = make_name_unique(
            slugified_aliases[aliases_by_nodeid[nodeid]], reserved_aliases, "_n"
        )
        reserved_aliases.add(new_alias)
        new_aliases_by_nodeid[nodeid] = new_alias
    return new_aliases_by_nodeid


def format_file_into_sql(file: str, sql_dir: str):
    sql_file = Path(__file__).parent / sql_dir / file
    sql_string = ""
    with open(sql_file) as file:
        sql_string = sql_string + "\n" + file.read()
    return sql_string


def get_system_settings_resource_model_id():
    from arches.app.models.system_settings import SystemSettings

    return SystemSettings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID
