from arches.app.utils.permission_backend import get_editable_resource_types
from arches.app.utils.permission_backend import get_createable_resource_types
from arches.app.utils.permission_backend import get_resource_types_by_perm
from django import template
import json

register = template.Library()


@register.filter(name="has_group")
def has_group(user, group_names):
    if user.is_authenticated:
        if user.is_superuser or bool(user.groups.filter(name__in=group_names.split(","))):
            return True
    return False


@register.filter(name="can_edit_resource_instance")
def can_edit_resource_instance(user):
    return len(get_editable_resource_types(user)) > 0


@register.filter(name="can_read_resource_instance")
def can_read_resource_instance(user):
    return len(get_resource_types_by_perm(user, ["models.write_nodegroup", "models.delete_nodegroup", "models.read_nodegroup"])) > 0


@register.filter(name="can_create_resource_instance")
def can_create_resource_instance(user):
    return len(get_createable_resource_types(user)) > 0


@register.filter(name="can_create_graph")
def can_create_graph(user):
    return len(get_resource_types_by_perm(user, ["models.write_nodegroup", "models.delete_nodegroup"])) > 0


@register.filter(name="has_key")
def has_dict_key(the_dict, key):
    """
    If the key has a space then template dot notation can't parse it e.g. resource.["Asset Name"]
    Provides a tag to handle an unparsable key check
    """
    value = False
    try:
        value = key in the_dict.keys()
    except:
        pass
    return value


@register.filter(name="val_from_key")
def dict_value_from_key(the_dict, key):
    """
    If the key has a space then template dot notation can't parse it e.g. resource.["Asset Name"]
    Provide a tag to handle fetching a value for an unparsable key
    """
    value = ""
    try:
        if key in the_dict.keys():
            value = the_dict[key]
    except:
        pass
    return value


@register.filter(name="json_to_obj")
def return_json_as_obj(string):
    """
    Allows a json value found in the template context to be converted into an object.
    """
    value = {}
    try:
        if isinstance(string, str):
            value = json.loads(string)
    except:
        pass
    return value
