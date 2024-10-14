from abc import abstractmethod, ABCMeta

from arches.app.const import ExtensionType
from arches.app.models.models import EditLog, GraphModel
from arches.app.models.system_settings import settings
from arches.app.utils.module_importer import get_class_from_modulename


class NotUserNorGroup(Exception): ...


class PermissionBackend:
    def __init__(self):
        self._backend = _get_permission_backend()

    def authenticate(self, request, username=None, password=None):
        return self._backend.authenticate(request, username=username, password=password)

    def has_perm(self, user_obj, perm, obj=None):
        return self._backend.has_perm(user_obj, perm, obj=obj)

    def get_all_permissions(self, user_obj, obj=None):
        return self._backend.get_all_permissions(user_obj, obj=obj)


def user_created_transaction(user, transactionid):
    if user.is_authenticated:
        if user.is_superuser:
            return True
        if EditLog.objects.filter(transactionid=transactionid).exists():
            if EditLog.objects.filter(
                transactionid=transactionid, userid=user.id
            ).exists():
                return True
        else:
            return True
    return False


class PermissionFramework(metaclass=ABCMeta):
    @abstractmethod
    def user_can_read_graph(self, user, graph_id): ...

    @abstractmethod
    def user_can_delete_model_nodegroups(self, user, resource): ...

    @abstractmethod
    def user_can_edit_model_nodegroups(self, user, resource): ...

    @abstractmethod
    def get_createable_resource_types(self, user): ...

    @abstractmethod
    def get_editable_resource_types(self, user): ...

    @abstractmethod
    def assign_perm(self, perm, user_or_group, obj=None): ...

    @abstractmethod
    def remove_perm(self, perm, user_or_group=None, obj=None): ...

    @abstractmethod
    def get_permission_backend(self): ...

    @abstractmethod
    def get_restricted_users(self, resource): ...

    @abstractmethod
    def get_filtered_instances(
        self, user, search_engine=None, allresources=False, resources=None
    ): ...

    @abstractmethod
    def get_groups_with_permission_for_object(self, perm, obj): ...

    @abstractmethod
    def get_users_with_permission_for_object(self, perm, obj): ...

    @abstractmethod
    def check_resource_instance_permissions(
        self, user, resourceid, permission, *, resource=None
    ): ...

    @abstractmethod
    def get_nodegroups_by_perm(self, user, perms, any_perm=True): ...

    @abstractmethod
    def get_map_layers_by_perm(self, user, perms, any_perm=True): ...

    @abstractmethod
    def user_can_read_map_layers(self, user): ...

    @abstractmethod
    def user_can_write_map_layers(self, user): ...

    @abstractmethod
    def process_new_user(self, instance, created): ...

    @abstractmethod
    def user_has_resource_model_permissions(self, user, perms, resource): ...

    @abstractmethod
    def user_can_read_resource(self, user, resourceid=None, *, resource=None): ...

    @abstractmethod
    def user_can_edit_resource(self, user, resourceid=None, *, resource=None): ...

    @abstractmethod
    def user_can_delete_resource(self, user, resourceid=None, *, resource=None): ...

    @abstractmethod
    def user_can_read_concepts(self, user): ...

    @abstractmethod
    def user_is_resource_editor(self, user): ...

    @abstractmethod
    def user_is_resource_reviewer(self, user): ...

    @abstractmethod
    def user_is_resource_exporter(self, user): ...

    @abstractmethod
    def get_resource_types_by_perm(self, user, perms): ...

    @abstractmethod
    def user_in_group_by_name(self, user, names): ...

    @abstractmethod
    def group_required(self, user, *group_names): ...

    @abstractmethod
    def update_mappings(self): ...

    @abstractmethod
    def get_index_values(self, resource): ...

    @abstractmethod
    def get_permission_inclusions(self): ...

    @abstractmethod
    def get_permission_search_filter(self, user): ...

    @abstractmethod
    def get_search_ui_permissions(self, user, search_result, groups=None): ...

    @abstractmethod
    def get_default_permissions(user_or_group, model): ...

    @abstractmethod
    def get_default_settable_permissions(self): ...


_PERMISSION_FRAMEWORK = None


def _get_permission_framework():
    global _PERMISSION_FRAMEWORK
    if not _PERMISSION_FRAMEWORK:
        if settings.PERMISSION_FRAMEWORK:
            if "." not in settings.PERMISSION_FRAMEWORK:
                raise RuntimeError(
                    "Permissions frameworks must be a dot-separated module and a class"
                )
            modulename, classname = settings.PERMISSION_FRAMEWORK.split(".", -1)
            PermissionFramework = get_class_from_modulename(
                modulename, classname, ExtensionType.PERMISSIONS_FRAMEWORKS
            )
            _PERMISSION_FRAMEWORK = PermissionFramework()
        else:
            from arches.app.permissions.arches_default_allow import (
                ArchesDefaultAllowPermissionFramework,
            )

            _PERMISSION_FRAMEWORK = ArchesDefaultAllowPermissionFramework()
    return _PERMISSION_FRAMEWORK


def get_createable_resource_models(user):
    return GraphModel.objects.filter(
        pk__in=list(get_createable_resource_types(user))
    ).all()


def assign_perm(perm, user_or_group, obj=None):
    return _get_permission_framework().assign_perm(perm, user_or_group, obj=obj)


def remove_perm(perm, user_or_group=None, obj=None):
    return _get_permission_framework().remove_perm(
        perm, user_or_group=user_or_group, obj=obj
    )


def _get_permission_backend():
    return _get_permission_framework().get_permission_backend()


def get_restricted_users(resource):
    return _get_permission_framework().get_restricted_users(resource)


def get_filtered_instances(
    user, search_engine=None, allresources=False, resources=list[str]
) -> tuple[bool, list[str]]:
    return _get_permission_framework().get_filtered_instances(
        user,
        search_engine=search_engine,
        allresources=allresources,
        resources=resources,
    )


def get_groups_with_permission_for_object(perm, obj):
    return _get_permission_framework().get_groups_with_permission_for_object(perm, obj)


def get_users_with_permission_for_object(perm, obj):
    return _get_permission_framework().get_users_with_permission_for_object(perm, obj)


def check_resource_instance_permissions(user, resourceid, permission, *, resource=None):
    return _get_permission_framework().check_resource_instance_permissions(
        user, resourceid, permission, resource=resource
    )


def get_nodegroups_by_perm(user, perms, any_perm=True):
    return _get_permission_framework().get_nodegroups_by_perm(
        user, perms, any_perm=any_perm
    )


def get_map_layers_by_perm(user, perms, any_perm=True):
    return _get_permission_framework().get_map_layers_by_perm(
        user, perms, any_perm=any_perm
    )


def user_can_read_map_layers(user):
    return _get_permission_framework().user_can_read_map_layers(user)


def user_can_write_map_layers(user):
    return _get_permission_framework().user_can_write_map_layers(user)


def get_users_with_perms(
    obj,
    attach_perms=False,
    with_superusers=False,
    with_group_users=True,
    only_with_perms_in=None,
):
    return _get_permission_framework().get_users_with_perms(
        obj,
        attach_perms=attach_perms,
        with_superusers=with_superusers,
        with_group_users=with_group_users,
        only_with_perms_in=only_with_perms_in,
    )


def get_groups_with_perms(obj, attach_perms=False):
    return _get_permission_framework().get_groups_with_perms(
        obj, attach_perms=attach_perms
    )


def get_user_perms(user, obj):
    """
    returns a queryset of permissions objects for a given user on a particular resource
    """
    return _get_permission_framework().get_user_perms(user, obj)


def get_group_perms(user_or_group, obj):
    """
    returns a queryset of permissions objects for a given group on a particular resource
    """
    return _get_permission_framework().get_group_perms(user_or_group, obj)


def get_perms_for_model(cls):
    return _get_permission_framework().get_perms_for_model(cls)


def get_perms(user_or_group, obj):
    return _get_permission_framework().get_perms(user_or_group, obj)


def process_new_user(instance, created):
    return _get_permission_framework().process_new_user(instance, created)


def update_groups_for_user(instance):
    return _get_permission_framework().update_groups_for_user(instance)


def update_permissions_for_user(instance):
    return _get_permission_framework().update_permissions_for_user(instance)


def update_permissions_for_group(instance):
    return _get_permission_framework().update_permissions_for_group(instance)


def user_has_resource_model_permissions(user, perms, resource):
    return _get_permission_framework().user_has_resource_model_permissions(
        user, perms, resource
    )


def user_can_read_resource(user, resourceid=None, *, resource=None):
    return _get_permission_framework().user_can_read_resource(
        user, resourceid=resourceid, resource=resource
    )


def user_can_edit_resource(user, resourceid=None, *, resource=None):
    return _get_permission_framework().user_can_edit_resource(
        user, resourceid=resourceid, resource=resource
    )


def user_can_delete_resource(user, resourceid=None, *, resource=None):
    return _get_permission_framework().user_can_delete_resource(
        user, resourceid=resourceid, resource=resource
    )


def user_can_read_concepts(user):
    return _get_permission_framework().user_can_read_concepts(user)


def user_is_resource_editor(user):
    return _get_permission_framework().user_is_resource_editor(user)


def user_is_resource_reviewer(user):
    return _get_permission_framework().user_is_resource_reviewer(user)


def user_is_resource_exporter(user):
    return _get_permission_framework().user_is_resource_exporter(user)


def get_resource_types_by_perm(user, perms):
    return _get_permission_framework().get_resource_types_by_perm(user, perms)


def user_in_group_by_name(user, names):
    return _get_permission_framework().user_in_group_by_name(user, names)


def user_can_read_graph(user, graph_id):
    return _get_permission_framework().user_can_read_graph(user, graph_id)


def user_can_delete_model_nodegroups(user, resource):
    return _get_permission_framework().user_can_delete_model_nodegroups(user, resource)


def user_can_edit_model_nodegroups(user, resource):
    return _get_permission_framework().user_can_edit_model_nodegroups(user, resource)


def get_createable_resource_types(user):
    return _get_permission_framework().get_createable_resource_types(user)


def get_editable_resource_types(user):
    return _get_permission_framework().get_editable_resource_types(user)


def group_required(user, *group_names):
    return _get_permission_framework().group_required(user, *group_names)


def update_mappings():
    return _get_permission_framework().update_mappings()


def get_index_values(resource):
    return _get_permission_framework().get_index_values(resource)


def get_permission_search_filter(user):
    return _get_permission_framework().get_permission_search_filter(user)


def get_permission_inclusions():
    return _get_permission_framework().get_permission_inclusions()


def get_search_ui_permissions(user, search_result, groups=None):
    return _get_permission_framework().get_search_ui_permissions(
        user, search_result, groups
    )


def get_default_permissions(
    user_or_group,
    model,
):
    return _get_permission_framework().get_default_permissions(user_or_group, model)


def get_default_settable_permissions():
    return _get_permission_framework().get_default_settable_permissions()
