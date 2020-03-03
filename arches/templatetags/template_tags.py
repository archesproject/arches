from arches.app.utils.permission_backend import get_editable_resource_types
from arches.app.utils.permission_backend import get_createable_resource_types
from arches.app.utils.permission_backend import get_resource_types_by_perm
from django import template

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
