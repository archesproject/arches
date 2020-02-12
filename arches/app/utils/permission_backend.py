from arches.app.models.models import Node
from arches.app.models.system_settings import settings
from guardian.backends import check_support
from guardian.backends import ObjectPermissionBackend
from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import get_perms, get_objects_for_user
from guardian.exceptions import WrongAppError
from django.contrib.auth.models import User, Group, Permission
from django.core.cache import cache

# Needs to be part of settings really
cache_timeout_secs = 120

class PermissionBackend(ObjectPermissionBackend):
    def has_perm(self, user_obj, perm, obj=None):
        # check if user_obj and object are supported (pulled directly from guardian)
        support, user_obj = check_support(user_obj, obj)
        if not support:
            return False

        if "." in perm:
            app_label, perm = perm.split(".")
            if app_label != obj._meta.app_label:
                raise WrongAppError("Passed perm has app label of '%s' and " "given obj has '%s'" % (app_label, obj._meta.app_label))

        explicitly_defined_perms = get_perms(user_obj, obj)
        if len(explicitly_defined_perms) > 0:
            if "no_access_to_nodegroup" in explicitly_defined_perms:
                return False
            else:
                return perm in explicitly_defined_perms
        else:
            default_perms = []
            for group in user_obj.groups.all():
                for permission in group.permissions.all():
                    if perm in permission.codename:
                        return True
            return False


def get_groups_for_object(perm, obj):
    """
    returns a list of group objects that have the given permission on the given object

    Arguments:
    perm -- the permssion string eg: "read_nodegroup"
    obj -- the model instance to check

    """

    def has_group_perm(group, perm, obj):
        explicitly_defined_perms = get_perms(group, obj)
        if len(explicitly_defined_perms) > 0:
            if "no_access_to_nodegroup" in explicitly_defined_perms:
                return False
            else:
                return perm in explicitly_defined_perms
        else:
            default_perms = []
            for permission in group.permissions.all():
                if perm in permission.codename:
                    return True
            return False

    ret = []
    for group in Group.objects.all():
        if has_group_perm(group, perm, obj):
            ret.append(group)
    return ret


def get_users_for_object(perm, obj):
    """
    returns a list of user objects that have the given permission on the given object

    Arguments:
    perm -- the permssion string eg: "read_nodegroup"
    obj -- the model instance to check

    """
    key = 'users_for_object_{0}_'.format(str(obj.pk)) + str("_".join(perm) if type(perm) == list else str(perm))    
    ret = cache.get(key)
    if ret is not None:
        return ret

    ret = []
    for user in User.objects.all():
        if user.has_perm(perm, obj):
            ret.append(user)
    
    cache.set(key, ret, cache_timeout_secs)
    return ret


def get_nodegroups_by_perm(user, perms, any_perm=True):
    """
    returns a list of node groups that a user has the given permission on

    Arguments:
    user -- the user to check
    perms -- the permssion string eg: "read_nodegroup" or list of strings
    any_perm -- True to check ANY perm in "perms" or False to check ALL perms

    """
    key = 'node_perms_{0}_'.format(user.username,) + str("_".join(perms) if type(perms) == list else str(perms))
    node_perms = cache.get(key)
    if node_perms is not None:
        return node_perms
    
    A = set(
        get_objects_for_user(
            user,
            ["models.read_nodegroup", "models.write_nodegroup", "models.delete_nodegroup", "models.no_access_to_nodegroup"],
            accept_global_perms=False,
            any_perm=True,
        )
    )
    B = set(get_objects_for_user(user, perms, accept_global_perms=False, any_perm=any_perm))
    C = set(get_objects_for_user(user, perms, accept_global_perms=True, any_perm=any_perm))
    
    node_perms = list(C - A | B)
    cache.set(key, node_perms, cache_timeout_secs)
    return node_perms


def get_editable_resource_types(user):
    """
    returns a list of graphs that a user can edit resource instances of

    Arguments:
    user -- the user to check

    """

    return get_resource_types_by_perm(user, ["models.write_nodegroup", "models.delete_nodegroup"])


def get_createable_resource_types(user):
    """
    returns a list of graphs that a user can create resource instances of

    Arguments:
    user -- the user to check

    """

    return get_resource_types_by_perm(user, "models.write_nodegroup")


def get_resource_types_by_perm(user, perms):
    """
    returns a list of graphs that a user have specific permissions on

    Arguments:
    user -- the user to check
    perms -- the permssion string eg: "read_nodegroup" or list of strings

    """
    key = 'get_resource_types_by_perm_{0}_'.format(user.username) + str("_".join(perms) if type(perms) == list else str(perms))
    graphlist = cache.get(key)
    if graphlist is not None:
        return graphlist
    
    graphs = set()
    nodegroups = get_nodegroups_by_perm(user, perms)
    for node in Node.objects.filter(nodegroup__in=nodegroups, graph__isresource=True).exclude(graph__graphid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID).select_related('graph'):
        graphs.add(node.graph)

    graphlist = list(graphs)
    cache.set(key, graphlist, cache_timeout_secs)

    return graphlist


def user_can_read_resources(user):
    """
    Requires that a user be able to read a single nodegroup of a resource

    """

    if user.is_authenticated:
        return user.is_superuser or len(get_resource_types_by_perm(user, ["models.read_nodegroup"])) > 0
    return False


def user_can_edit_resources(user):
    """
    Requires that a user be able to edit or delete a single nodegroup of a resource

    """

    if user.is_authenticated:
        return (
            user.is_superuser
            or len(get_editable_resource_types(user)) > 0
            or user.groups.filter(name__in=settings.RESOURCE_EDITOR_GROUPS).exists()
        )
    return False


def user_can_read_concepts(user):
    """
    Requires that a user is a part of the RDM Administrator group

    """

    if user.is_authenticated:
        return user.groups.filter(name="RDM Administrator").exists()
    return False


def user_is_resource_reviewer(user):
    """
    Single test for whether a user is in the Resource Reviewer group
    """

    return user.groups.filter(name='Resource Reviewer').exists()
