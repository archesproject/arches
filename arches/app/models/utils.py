import warnings
from pathlib import Path


PRIOR_UPDATE_FIELDS_SENTINEL = []
FUTURE_UPDATE_FIELDS_SENTINEL = []


def add_to_update_fields(kwargs, field_name):
    """Return new kwargs with any `update_field` kwarg augmented with `field_name`."""
    # When the future comes, replace all of this with just:
    # if update_fields := kwargs.get("update_fields"):
    #     return {
    #         **kwargs,
    #         "update_fields": {*update_fields, field_name},
    #     }
    # return kwargs

    update_fields = kwargs.get("update_fields")
    if (
        not update_fields
        and update_fields is not None
        and update_fields is not FUTURE_UPDATE_FIELDS_SENTINEL
    ):
        # Empty iterable. Handle like None for now, but issue a warning.
        # https://forum.djangoproject.com/t/update-or-create-defaults-none-sends-update-fields-set-rather-than-none/41657/4
        warnings.warn(
            "You likely called update_or_create() without specifying "
            f"{field_name} in `defaults`.\n"
            "In the future, you will not be able to depend on model "
            f"save() logic injecting {field_name} without explicitly "
            "opting in by providing some preliminary value for it via `defaults`.",
            FutureWarning,
            stacklevel=5,
        )
        update_fields = PRIOR_UPDATE_FIELDS_SENTINEL
    if update_fields or update_fields is PRIOR_UPDATE_FIELDS_SENTINEL:
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


def format_file_into_sql(file: str, sql_dir: str):
    sql_file = Path(__file__).parent / sql_dir / file
    sql_string = ""
    with open(sql_file) as file:
        sql_string = sql_string + "\n" + file.read()
    return sql_string


def get_system_settings_resource_model_id():
    from arches.app.models.system_settings import SystemSettings

    return SystemSettings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID
