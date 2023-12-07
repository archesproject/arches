from django.core.exceptions import ObjectDoesNotExist
from arches.app.models.system_settings import settings
from django.contrib.auth.models import User, Group
from django.contrib.gis.db.models import Model
from django.core.cache import caches
from guardian.backends import check_support, ObjectPermissionBackend
from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import (
    get_perms,
    get_group_perms,
    get_user_perms,
    get_users_with_perms,
    get_groups_with_perms,
    get_perms_for_model,
)
from guardian.exceptions import NotUserNorGroup
from arches.app.models.resource import Resource

from guardian.models import GroupObjectPermission, UserObjectPermission
from guardian.exceptions import WrongAppError
from guardian.shortcuts import assign_perm, get_perms, remove_perm, get_group_perms, get_user_perms

import inspect
from arches.app.models.models import *
from arches.app.models.models import ResourceInstance, MapLayer
from arches.app.search.elasticsearch_dsl_builder import Bool, Query, Terms, Nested
from arches.app.search.mappings import RESOURCES_INDEX
from arches.app.utils.permission_backend import PermissionFramework, NotUserNorGroup as ArchesNotUserNorGroup

class ArchesStandardPermissionFramework(PermissionFramework):
    def setup(self):
        ...

    def get_perms_for_model(self, cls):
        return get_perms_for_model(cls)

    def assign_perm(self, perm, user_or_group, obj=None):
        try:
            return assign_perm(perm, user_or_group, obj=obj)
        except NotUserNorGroup:
            raise ArchesNotUserNorGroup()

    def get_permission_backend(self):
        return PermissionBackend()

    def remove_perm(self, perm, user_or_group=None, obj=None):
        return remove_perm(perm, user_or_group=user_or_group, obj=obj)

    def get_perms(self, user_or_group, obj):
        return get_perms(user_or_group, obj)

    def get_group_perms(self, user_or_group, obj):
        return get_group_perms(user_or_group, obj)

    def get_user_perms(self, user, obj):
        return get_user_perms(user, obj)

    def process_new_user(self, instance, created):
        ct = ContentType.objects.get(app_label="models", model="resourceinstance")
        resourceInstanceIds = list(GroupObjectPermission.objects.filter(content_type=ct).values_list("object_pk", flat=True).distinct())
        for resourceInstanceId in resourceInstanceIds:
            resourceInstanceId = uuid.UUID(resourceInstanceId)
        resources = ResourceInstance.objects.filter(pk__in=resourceInstanceIds)
        self.assign_perm("no_access_to_resourceinstance", instance, resources)
        for resource_instance in resources:
            resource = Resource(resource_instance.resourceinstanceid)
            resource.graph_id = resource_instance.graph_id
            resource.createdtime = resource_instance.createdtime
            resource.index()

    def get_map_layers_by_perm(self, user, perms, any_perm=True):
        """
        returns a list of node groups that a user has the given permission on

        Arguments:
        user -- the user to check
        perms -- the permssion string eg: "read_map_layer" or list of strings
        any_perm -- True to check ANY perm in "perms" or False to check ALL perms

        """

        if not isinstance(perms, list):
                perms = [perms]

        formatted_perms = []
        # in some cases, `perms` can have a `model.` prefix
        for perm in perms:
            if len(perm.split(".")) > 1:
                formatted_perms.append(perm.split(".")[1])
            else:
                formatted_perms.append(perm)

        if user.is_superuser is True:
            return MapLayer.objects.all()
        else:
            permitted_map_layers = list()

            user_permissions = ObjectPermissionChecker(user)

            for map_layer in MapLayer.objects.all():
                if map_layer.addtomap is True and map_layer.isoverlay is False:
                    permitted_map_layers.append(map_layer)
                else:  # if no explicit permissions, object is considered accessible by all with group permissions
                    explicit_map_layer_perms = user_permissions.get_perms(map_layer)
                    if len(explicit_map_layer_perms):
                        if any_perm:
                            if len(set(formatted_perms) & set(explicit_map_layer_perms)):
                                permitted_map_layers.append(map_layer)
                        else:
                            if set(formatted_perms) == set(explicit_map_layer_perms):
                                permitted_map_layers.append(map_layer)
                    elif map_layer.ispublic:
                        permitted_map_layers.append(map_layer)

            return permitted_map_layers


    def user_can_read_map_layers(self, user):

        map_layers_with_read_permission = self.get_map_layers_by_perm(user, ["models.read_maplayer"])
        map_layers_allowed = []

        for map_layer in map_layers_with_read_permission:
            if ("no_access_to_maplayer" not in get_user_perms(user, map_layer)) or (
                map_layer.addtomap is False and map_layer.isoverlay is False
            ):
                map_layers_allowed.append(map_layer)

        return map_layers_allowed


    def user_can_write_map_layers(self, user):
        map_layers_with_write_permission = self.get_map_layers_by_perm(user, ["models.write_maplayer"])
        map_layers_allowed = []

        for map_layer in map_layers_with_write_permission:
            if ("no_access_to_maplayer" not in get_user_perms(user, map_layer)) or (
                map_layer.addtomap is False and map_layer.isoverlay is False
            ):
                map_layers_allowed.append(map_layer)

        return map_layers_allowed

    def get_nodegroups_by_perm(self, user, perms, any_perm=True):
        """
        returns a list of node groups that a user has the given permission on

        Arguments:
        user -- the user to check
        perms -- the permssion string eg: "read_nodegroup" or list of strings
        any_perm -- True to check ANY perm in "perms" or False to check ALL perms

        """
        if not isinstance(perms, list):
            perms = [perms]

        formatted_perms = []
        # in some cases, `perms` can have a `model.` prefix
        for perm in perms:
            if len(perm.split(".")) > 1:
                formatted_perms.append(perm.split(".")[1])
            else:
                formatted_perms.append(perm)

        permitted_nodegroups = set()
        NodegroupPermissionsChecker = CachedObjectPermissionChecker(user, NodeGroup)

        for nodegroup in NodeGroup.objects.all():
            explicit_perms = NodegroupPermissionsChecker.get_perms(nodegroup)

            if len(explicit_perms):
                if any_perm:
                    if len(set(formatted_perms) & set(explicit_perms)):
                        permitted_nodegroups.add(nodegroup)
                else:
                    if set(formatted_perms) == set(explicit_perms):
                        permitted_nodegroups.add(nodegroup)
            else:  # if no explicit permissions, object is considered accessible by all with group permissions
                permitted_nodegroups.add(nodegroup)

        return permitted_nodegroups

    def check_resource_instance_permissions(self, user, resourceid, permission):
        """
        Checks if a user has permission to access a resource instance

        Arguments:
        user -- the user to check
        resourceid -- the id of the resource
        permission -- the permission codename (e.g. 'view_resourceinstance') for which to check

        """
        result = {}
        try:
            if resourceid == settings.SYSTEM_SETTINGS_RESOURCE_ID:
                if not user.groups.filter(name="System Administrator").exists():
                    result["permitted"] = False
                    return result

            resource = ResourceInstance.objects.get(resourceinstanceid=resourceid)
            result["resource"] = resource

            all_perms = self.get_perms(user, resource)

            if len(all_perms) == 0:  # no permissions assigned. permission implied
                result["permitted"] = "unknown"
                return result
            else:
                user_permissions = self.get_user_perms(user, resource)
                if "no_access_to_resourceinstance" in user_permissions:  # user is restricted
                    result["permitted"] = False
                    return result
                elif permission in user_permissions:  # user is permitted
                    result["permitted"] = True
                    return result

                group_permissions = self.get_group_perms(user, resource)
                if "no_access_to_resourceinstance" in group_permissions:  # group is restricted - no user override
                    result["permitted"] = False
                    return result
                elif permission in group_permissions:  # group is permitted - no user override
                    result["permitted"] = True
                    return result

                if permission not in all_perms:  # neither user nor group explicitly permits or restricts.
                    result["permitted"] = False  # restriction implied
                    return result

        except ObjectDoesNotExist:
            result["permitted"] = True # if the object does not exist, no harm in returning true - this prevents strange 403s.
            return result

        return result

    def get_users_with_perms(self, obj, attach_perms=False, with_superusers=False, with_group_users=True, only_with_perms_in=None):
        return get_users_with_perms(obj, attach_perms=attach_perms, with_superusers=with_superusers, with_group_users=with_group_users, only_with_perms_in=only_with_perms_in)

    def get_groups_with_perms(self, obj, attach_perms=False):
        return get_groups_with_perms(obj, attach_perms=attach_perms)

    def get_restricted_users(self, resource):
        """
        Takes a resource instance and identifies which users are explicitly restricted from
        reading, editing, deleting, or accessing it.

        """

        user_perms = get_users_with_perms(resource, attach_perms=True, with_group_users=False)
        user_and_group_perms = get_users_with_perms(resource, attach_perms=True, with_group_users=True)

        result = {
            "no_access": [],
            "cannot_read": [],
            "cannot_write": [],
            "cannot_delete": [],
        }

        for user, perms in user_and_group_perms.items():
            if user.is_superuser:
                pass
            elif user in user_perms and "no_access_to_resourceinstance" in user_perms[user]:
                for k, v in result.items():
                    v.append(user.id)
            else:
                if "view_resourceinstance" not in perms:
                    result["cannot_read"].append(user.id)
                if "change_resourceinstance" not in perms:
                    result["cannot_write"].append(user.id)
                if "delete_resourceinstance" not in perms:
                    result["cannot_delete"].append(user.id)
                if "no_access_to_resourceinstance" in perms and len(perms) == 1:
                    result["no_access"].append(user.id)

        return result

    def get_groups_for_object(self, perm, obj):
        """
        returns a list of group objects that have the given permission on the given object

        Arguments:
        perm -- the permssion string eg: "read_nodegroup"
        obj -- the model instance to check

        """

        def has_group_perm(group, perm, obj):
            explicitly_defined_perms = self.get_perms(group, obj)
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


    def get_users_for_object(self, perm, obj):
        """
        Returns a list of user objects that have the given permission on the given object

        Arguments:
        perm -- the permssion string eg: "read_nodegroup"
        obj -- the model instance to check

        """

        ret = []
        for user in User.objects.all():
            if user.has_perm(perm, obj):
                ret.append(user)
        return ret


    def get_restricted_instances(self, user, search_engine=None, allresources=False):
        if allresources is False and user.is_superuser is True:
            return []

        if allresources is True:
            restricted_group_instances = {
                perm["object_pk"]
                for perm in GroupObjectPermission.objects.filter(permission__codename="no_access_to_resourceinstance").values("object_pk")
            }
            restricted_user_instances = {
                perm["object_pk"]
                for perm in UserObjectPermission.objects.filter(permission__codename="no_access_to_resourceinstance").values("object_pk")
            }
            all_restricted_instances = list(restricted_group_instances | restricted_user_instances)
            return all_restricted_instances
        else:
            terms = Terms(field="permissions.users_with_no_access", terms=[str(user.id)])
            query = Query(search_engine, start=0, limit=settings.SEARCH_RESULT_LIMIT)
            has_access = Bool()
            nested_term_filter = Nested(path="permissions", query=terms)
            has_access.must(nested_term_filter)
            query.add_query(has_access)
            results = query.search(index=RESOURCES_INDEX, scroll="1m")
            scroll_id = results["_scroll_id"]
            total = results["hits"]["total"]["value"]
            if total > settings.SEARCH_RESULT_LIMIT:
                pages = total // settings.SEARCH_RESULT_LIMIT
                for page in range(pages):
                    results_scrolled = query.se.es.scroll(scroll_id=scroll_id, scroll="1m")
                    results["hits"]["hits"] += results_scrolled["hits"]["hits"]
            restricted_ids = [res["_id"] for res in results["hits"]["hits"]]
            return restricted_ids

    def update_groups_for_user(self, user):
        """Hook for spotting group updates on a user."""
        ...

    def update_permissions_for_user(self, user):
        """Hook for spotting permission updates on a user."""
        ...

    def update_permissions_for_group(self, group):
        """Hook for spotting permission updates on a group."""
        ...



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

        ObjPermissionChecker = CachedObjectPermissionChecker(user_obj, obj)
        explicitly_defined_perms = ObjPermissionChecker.get_perms(obj)

        if len(explicitly_defined_perms) > 0:
            if "no_access_to_nodegroup" in explicitly_defined_perms:
                return False
            else:
                return bool(perm in explicitly_defined_perms)
        else:
            UserPermissionChecker = CachedUserPermissionChecker(user_obj)
            return bool(UserPermissionChecker.user_has_permission(perm))


class CachedUserPermissionChecker:
    """
    A permission checker that leverages the 'user_permission' cache to check user-level user permissions.
    """

    def __init__(self, user):
        user_permission_cache = caches["user_permission"]
        current_user_cached_permissions = user_permission_cache.get(str(user.pk), {})

        if current_user_cached_permissions.get("user_permissions"):
            user_permissions = current_user_cached_permissions.get("user_permissions")
        else:
            user_permissions = set()

            for group in user.groups.all():
                for group_permission in group.permissions.all():
                    user_permissions.add(group_permission.codename)

            for user_permission in user.user_permissions.all():
                user_permissions.add(user_permission.codename)

            current_user_cached_permissions["user_permissions"] = user_permissions
            user_permission_cache.set(str(user.pk), current_user_cached_permissions)

        self.user_permissions = user_permissions

    def user_has_permission(self, permission):
        if permission in self.user_permissions:
            return True
        else:
            return False

class CachedObjectPermissionChecker:
    """
    A permission checker that leverages the 'user_permission' cache to check object-level user permissions.
    """

    def __new__(cls, user, input):
        if inspect.isclass(input):
            classname = input.__name__
        elif isinstance(input, Model):
            classname = input.__class__.__name__
        elif isinstance(input, str) and globals().get(input):
            classname = input
        else:
            raise Exception("Cannot derive model from input.")

        user_permission_cache = caches["user_permission"]

        current_user_cached_permissions = user_permission_cache.get(str(user.pk), {})

        if current_user_cached_permissions.get(classname):
            checker = current_user_cached_permissions.get(classname)
        else:
            checker = ObjectPermissionChecker(user)
            checker.prefetch_perms(globals()[classname].objects.all())

            current_user_cached_permissions[classname] = checker
            user_permission_cache.set(str(user.pk), current_user_cached_permissions)

        return checker
