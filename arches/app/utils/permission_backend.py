from abc import abstractmethod
import inspect

from arches.app.models.models import *
from arches.app.models.system_settings import settings

class NotUserNorGroup(Exception):
    ...


class PermissionBackend:
    def __init__(self):
        self._backend = _get_permission_backend()

    def authenticate(self, request, username=None, password=None):
        return self._backend.authenticate(request, username=username, password=password)

    def has_perm(self, user_obj, perm, obj=None):
        return self._backend.has_perm(user_obj, perm, obj=obj)

    def get_all_permissions(self, user_obj, obj=None):
        return self._backend.get_all_permissions(user_obj, obj=obj)


def get_editable_resource_types(user):
    """
    returns a list of graphs of which a user can edit resource instances

    Arguments:
    user -- the user to check

    """

    if user_is_resource_editor(user):
        return get_resource_types_by_perm(user, ["models.write_nodegroup", "models.delete_nodegroup"])
    else:
        return []


def get_createable_resource_types(user):
    """
    returns a list of graphs of which a user can create resource instances

    Arguments:
    user -- the user to check

    """
    if user_is_resource_editor(user):
        return get_resource_types_by_perm(user, "models.write_nodegroup")
    else:
        return []


def get_resource_types_by_perm(user, perms):
    """
    returns a list of graphs for which a user has specific nodegroup permissions

    Arguments:
    user -- the user to check
    perms -- the permssion string eg: "read_nodegroup" or list of strings
    resource -- a resource instance to check if a user has permissions to that resource's type specifically

    """

    graphs = set()
    nodegroups = get_nodegroups_by_perm(user, perms)
    for node in Node.objects.filter(nodegroup__in=nodegroups).prefetch_related("graph"):
        if node.graph.isresource and str(node.graph_id) != settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID:
            graphs.add(node.graph)
    return list(graphs)


def user_can_edit_model_nodegroups(user, resource):
    """
    returns a list of graphs of which a user can edit resource instances

    Arguments:
    user -- the user to check
    resource -- an instance of a model

    """

    return user_has_resource_model_permissions(user, ["models.write_nodegroup"], resource)


def user_can_delete_model_nodegroups(user, resource):
    """
    returns a list of graphs of which a user can edit resource instances

    Arguments:
    user -- the user to check
    resource -- an instance of a model

    """

    return user_has_resource_model_permissions(user, ["models.delete_nodegroup"], resource)


def user_has_resource_model_permissions(user, perms, resource):
    """
    Checks if a user has any explicit permissions to a model's nodegroups

    Arguments:
    user -- the user to check
    perms -- the permssion string eg: "read_nodegroup" or list of strings
    resource -- a resource instance to check if a user has permissions to that resource's type specifically

    """

    nodegroups = get_nodegroups_by_perm(user, perms)
    nodes = Node.objects.filter(nodegroup__in=nodegroups).filter(graph_id=resource.graph_id).select_related("graph")
    return nodes.exists()


def user_can_read_resource(user, resourceid=None):
    """
    Requires that a user be able to read an instance and read a single nodegroup of a resource

    """
    if user.is_authenticated:
        if user.is_superuser:
            return True
        if resourceid not in [None, ""]:
            result = check_resource_instance_permissions(user, resourceid, "view_resourceinstance")
            if result is not None:
                if result["permitted"] == "unknown":
                    return user_has_resource_model_permissions(user, ["models.read_nodegroup"], result["resource"])
                else:
                    return result["permitted"]
            else:
                return None

        return len(get_resource_types_by_perm(user, ["models.read_nodegroup"])) > 0
    return False


def user_can_edit_resource(user, resourceid=None):
    """
    Requires that a user be able to edit an instance and delete a single nodegroup of a resource

    """
    if user.is_authenticated:
        if user.is_superuser:
            return True
        if resourceid not in [None, ""]:
            result = check_resource_instance_permissions(user, resourceid, "change_resourceinstance")
            if result is not None:
                if result["permitted"] == "unknown":
                    return user.groups.filter(name__in=settings.RESOURCE_EDITOR_GROUPS).exists() or user_can_edit_model_nodegroups(
                        user, result["resource"]
                    )
                else:
                    return result["permitted"]
            else:
                return None

        return user.groups.filter(name__in=settings.RESOURCE_EDITOR_GROUPS).exists() or len(get_editable_resource_types(user)) > 0
    return False


def user_can_delete_resource(user, resourceid=None):
    """
    Requires that a user be permitted to delete an instance

    """
    if user.is_authenticated:
        if user.is_superuser:
            return True
        if resourceid not in [None, ""]:
            result = check_resource_instance_permissions(user, resourceid, "delete_resourceinstance")
            if result is not None:
                if result["permitted"] == "unknown":
                    nodegroups = get_nodegroups_by_perm(user, "models.delete_nodegroup")
                    tiles = TileModel.objects.filter(resourceinstance_id=resourceid)
                    protected_tiles = {str(tile.nodegroup_id) for tile in tiles} - {str(nodegroup.nodegroupid) for nodegroup in nodegroups}
                    if len(protected_tiles) > 0:
                        return False
                    return user.groups.filter(name__in=settings.RESOURCE_EDITOR_GROUPS).exists() or user_can_delete_model_nodegroups(
                        user, result["resource"]
                    )
                else:
                    return result["permitted"]
            else:
                return None
    return False


def user_can_read_concepts(user):
    """
    Requires that a user is a part of the RDM Administrator group

    """

    if user.is_authenticated:
        return user.groups.filter(name="RDM Administrator").exists()
    return False


def user_is_resource_editor(user):
    """
    Single test for whether a user is in the Resource Editor group
    """

    return user.groups.filter(name="Resource Editor").exists()


def user_is_resource_reviewer(user):
    """
    Single test for whether a user is in the Resource Reviewer group
    """

    return user.groups.filter(name="Resource Reviewer").exists()


def user_is_resource_exporter(user):
    """
    Single test for whether a user is in the Resource Exporter group
    """

    return user.groups.filter(name="Resource Exporter").exists()


def user_created_transaction(user, transactionid):
    if user.is_authenticated:
        if user.is_superuser:
            return True
        if EditLog.objects.filter(transactionid=transactionid).exists():
            if EditLog.objects.filter(transactionid=transactionid, userid=user.id).exists():
                return True
        else:
            return True
    return False

class PermissionFramework(metaclass=ABCMeta):
    @abstractmethod
    def assign_perm(self, perm, user_or_group, obj=None):
        ...

    @abstractmethod
    def remove_perm(self, perm, user_or_group=None, obj=None):
        ...

    @abstractmethod
    def get_permission_backend(self):
        ...

    @abstractmethod
    def get_restricted_users(self, resource):
        ...

    @abstractmethod
    def get_restricted_instances(self, user, search_engine=None, allresources=False):
        ...

    @abstractmethod
    def get_groups_for_object(self, perm, obj):
        ...

    @abstractmethod
    def get_users_for_object(self, perm, obj):
        ...

    @abstractmethod
    def check_resource_instance_permissions(self, user, resourceid, permission):
        ...

    @abstractmethod
    def get_nodegroups_by_perm(self, user, perms, any_perm=True):
        ...

    @abstractmethod
    def get_map_layers_by_perm(self, user, perms, any_perm=True):
        ...

    @abstractmethod
    def user_can_read_map_layers(self, user):
        ...

    @abstractmethod
    def user_can_write_map_layers(self, user):
        ...

    @abstractmethod
    def process_new_user(self, instance, created):
        ...

_PERMISSION_FRAMEWORK = None

def _get_permission_framework():
    global _PERMISSION_FRAMEWORK
    if not _PERMISSION_FRAMEWORK:
        if settings.PERMISSION_FRAMEWORK == "arches_default_deny":
            from arches.app.utils.permissions.arches_standard import ArchesDefaultDenyPermissionFramework
            _PERMISSION_FRAMEWORK = ArchesDefaultDenyPermissionFramework()
        else:
            from arches.app.utils.permissions.arches_standard import ArchesStandardPermissionFramework
            _PERMISSION_FRAMEWORK = ArchesStandardPermissionFramework()
    return _PERMISSION_FRAMEWORK

def assign_perm(perm, user_or_group, obj=None):
    return _get_permission_framework().assign_perm(perm, user_or_group, obj=obj)

def remove_perm(perm, user_or_group=None, obj=None):
    return _get_permission_framework().remove_perm(perm, user_or_group=user_or_group, obj=obj)

def _get_permission_backend():
    return _get_permission_framework().get_permission_backend()

def get_restricted_users(resource):
    return _get_permission_framework().get_restricted_users(resource)

def get_restricted_instances(user, search_engine=None, allresources=False):
    return _get_permission_framework().get_restricted_instances(user, search_engine=search_engine, allresources=allresources)

def get_groups_for_object(perm, obj):
    return _get_permission_framework().get_groups_for_object(perm, obj)

def get_users_for_object(perm, obj):
    return _get_permission_framework().get_users_for_object(perm, obj)

def check_resource_instance_permissions(user, resourceid, permission):
    return _get_permission_framework().check_resource_instance_permissions(user, resourceid, permission)

def get_nodegroups_by_perm(user, perms, any_perm=True):
    return _get_permission_framework().get_nodegroups_by_perm(user, perms, any_perm=any_perm)

def get_map_layers_by_perm(user, perms, any_perm=True):
    return _get_permission_framework().get_map_layers_by_perm(user, perms, any_perm=any_perm)

def user_can_read_map_layers(user):
    return _get_permission_framework().user_can_read_map_layers(user)

def user_can_write_map_layers(user):
    return _get_permission_framework().user_can_write_map_layers(user)

def process_new_user(instance, created):
    return _get_permission_framework().process_new_user(instance, created)
