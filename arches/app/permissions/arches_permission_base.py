"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.
You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
import sys
import uuid
from typing import Iterable

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, Group, Permission
from django.contrib.gis.db.models import Model
from django.core.cache import caches
from django.db.models import Count
from guardian.backends import check_support, ObjectPermissionBackend
from guardian.core import ObjectPermissionChecker
from guardian.exceptions import NotUserNorGroup
from arches.app.models.resource import Resource
from django.db.models.query import QuerySet
from guardian.models import GroupObjectPermission, UserObjectPermission, Permission
from guardian.exceptions import WrongAppError
from guardian.shortcuts import (
    get_perms,
    get_group_perms,
    get_user_perms,
    get_users_with_perms,
    get_groups_with_perms,
    get_perms_for_model,
    assign_perm,
    remove_perm,
)

import inspect
from arches.app.models.models import *
from arches.app.models.system_settings import settings
from arches.app.models.models import ResourceInstance, MapLayer

from arches.app.search.elasticsearch_dsl_builder import Bool, Query, Terms, Nested
from arches.app.search.mappings import RESOURCES_INDEX
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.utils.permission_backend import (
    PermissionFramework,
    NotUserNorGroup as ArchesNotUserNorGroup,
)
from arches.app.search.search import SearchEngine

if sys.version_info >= (3, 11):
    from typing import NotRequired, TypedDict, Literal

    class ResourceInstancePermissions(TypedDict):
        permitted: NotRequired[bool | Literal["unknown"]]
        resource: NotRequired[ResourceInstance]

else:
    ResourceInstancePermissions = dict

from datetime import datetime


class ArchesPermissionBase(PermissionFramework, metaclass=ABCMeta):
    def setup(self): ...

    def get_perms_for_model(self, cls: str | Model) -> list[Permission]:
        return self.get_default_permissions_objects(cls) | get_perms_for_model(cls)  # type: ignore

    def assign_perm(
        self,
        perm: Permission | str,
        user_or_group: User | Group,
        obj: ResourceInstance | None = None,
    ) -> Permission:
        try:
            return assign_perm(perm, user_or_group, obj=obj)
        except NotUserNorGroup:
            raise ArchesNotUserNorGroup()

    def get_permission_backend(self):
        return PermissionBackend()

    def remove_perm(self, perm, user_or_group=None, obj=None):
        return remove_perm(perm, user_or_group=user_or_group, obj=obj)

    def process_new_user(self, instance: User, created: bool) -> None:
        pass

    def get_perms(
        self, user_or_group: User | Group, obj: ResourceInstance
    ) -> list[str]:
        return self.get_default_permissions(user_or_group, obj, all_permissions=True) + get_perms(user_or_group, obj)  # type: ignore

    def get_group_perms(
        self, user_or_group: User | Group, obj: ResourceInstance
    ) -> QuerySet[Permission]:
        return self.get_default_permissions_objects(user_or_group, obj) | get_group_perms(user_or_group, obj)  # type: ignore

    def get_user_perms(self, user: User, obj: ResourceInstance) -> QuerySet[Permission]:
        return self.get_default_permissions_objects(user, obj) | get_user_perms(
            user, obj
        )

    def get_map_layers_by_perm(
        self, user: User, perms: str | Iterable[str], any_perm: bool = True
    ) -> list[MapLayer]:
        """
        returns a list of node groups that a user has the given permission on

        Arguments:
        user -- the user to check
        perms -- the permission string eg: "read_map_layer" or list of strings
        any_perm -- True to check ANY perm in "perms" or False to check ALL perms

        """

        if isinstance(perms, str):
            perms = [perms]

        formatted_perms = []
        # in some cases, `perms` can have a `model.` prefix
        for perm in perms:
            if len(perm.split(".")) > 1:
                formatted_perms.append(perm.split(".")[1])
            else:
                formatted_perms.append(perm)

        if user.is_superuser is True:
            return list(MapLayer.objects.all())
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
                            if len(
                                set(formatted_perms) & set(explicit_map_layer_perms)
                            ):
                                permitted_map_layers.append(map_layer)
                        else:
                            if set(formatted_perms) == set(explicit_map_layer_perms):
                                permitted_map_layers.append(map_layer)
                    elif map_layer.ispublic:
                        permitted_map_layers.append(map_layer)

            return permitted_map_layers

    def user_can_read_map_layers(self, user):
        map_layers_with_read_permission = self.get_map_layers_by_perm(
            user, ["models.read_maplayer"]
        )
        map_layers_allowed = []

        for map_layer in map_layers_with_read_permission:
            if ("no_access_to_maplayer" not in get_user_perms(user, map_layer)) or (
                map_layer.addtomap is False and map_layer.isoverlay is False
            ):
                map_layers_allowed.append(map_layer)

        return map_layers_allowed

    def user_can_write_map_layers(self, user: User) -> list[MapLayer]:
        map_layers_with_write_permission = self.get_map_layers_by_perm(
            user, ["models.write_maplayer"]
        )
        map_layers_allowed = []

        for map_layer in map_layers_with_write_permission:
            if ("no_access_to_maplayer" not in get_user_perms(user, map_layer)) or (
                map_layer.addtomap is False and map_layer.isoverlay is False
            ):
                map_layers_allowed.append(map_layer)

        return map_layers_allowed

    def get_nodegroups_by_perm(
        self, user: User, perms: str | Iterable[str], any_perm: bool = True
    ) -> list[uuid.UUID]:
        """
        returns a list of node groups that a user has the given permission on

        Arguments:
        user -- the user to check
        perms -- the permission string eg: "read_nodegroup" or list of strings
        any_perm -- True to check ANY perm in "perms" or False to check ALL perms

        """
        return list(
            set(
                nodegroup.pk
                for nodegroup in get_nodegroups_by_perm_for_user_or_group(
                    user, perms, any_perm=any_perm
                )
            )
        )

    def get_users_with_perms(
        self,
        obj: Model,
        attach_perms: bool = False,
        with_superusers: bool = False,
        with_group_users: bool = True,
        only_with_perms_in: Iterable[str] | None = None,
    ) -> list[User]:
        return get_users_with_perms(obj, attach_perms=attach_perms, with_superusers=with_superusers, with_group_users=with_group_users, only_with_perms_in=only_with_perms_in)  # type: ignore

    def get_groups_with_perms(
        self, obj: Model, attach_perms: bool = False
    ) -> list[Group]:
        return get_groups_with_perms(obj, attach_perms=attach_perms)  # type: ignore

    @abstractmethod
    def has_group_perm(self, group, perm, obj): ...

    @abstractmethod
    def check_resource_instance_permissions(
        self, user: User, resourceid: str, permission: str
    ): ...

    def get_groups_with_permission_for_object(
        self, perm: str, obj: Model
    ) -> list[Group]:
        """
        returns a list of group objects that have the given permission on the given object

        Arguments:
        perm -- the permission string eg: "read_nodegroup"
        obj -- the model instance to check

        """

        ret = []
        for group in Group.objects.all():
            if self.has_group_perm(group, perm, obj):  # type: ignore
                ret.append(group)
        return ret

    def get_users_with_permission_for_object(self, perm: str, obj: Model) -> list[User]:
        """
        Returns a list of user objects that have the given permission on the given object

        Arguments:
        perm -- the permission string eg: "read_nodegroup"
        obj -- the model instance to check

        """

        ret = []
        for user in User.objects.all():
            default_perms = self.get_default_permissions(user, obj)
            if user.has_perm(perm, obj) or perm in default_perms:
                ret.append(user)
        return ret

    def get_restricted_instances(
        self,
        user: User,
        search_engine: SearchEngine | None = None,
        allresources: bool = False,
    ) -> list[str]:
        if allresources is False and user.is_superuser is True:
            return []

        if allresources is True:
            restricted_group_instances = {
                perm["object_pk"]
                for perm in GroupObjectPermission.objects.filter(
                    permission__codename="no_access_to_resourceinstance"
                ).values("object_pk")
            }
            restricted_user_instances = {
                perm["object_pk"]
                for perm in UserObjectPermission.objects.filter(
                    permission__codename="no_access_to_resourceinstance"
                ).values("object_pk")
            }
            all_restricted_instances = list(
                restricted_group_instances | restricted_user_instances
            )
            return all_restricted_instances
        else:
            terms = Terms(field="permissions.users_with_no_access", terms=[str(user.id)])  # type: ignore
            query = Query(search_engine, start=0, limit=settings.SEARCH_RESULT_LIMIT)  # type: ignore
            has_access = Bool()  # type: ignore
            nested_term_filter = Nested(path="permissions", query=terms)  # type: ignore
            has_access.must(nested_term_filter)  # type: ignore
            query.add_query(has_access)  # type: ignore
            results = query.search(index=RESOURCES_INDEX, scroll="1m")  # type: ignore
            scroll_id = results["_scroll_id"]
            total = results["hits"]["total"]["value"]
            if total > settings.SEARCH_RESULT_LIMIT:
                pages = total // settings.SEARCH_RESULT_LIMIT
                for page in range(pages):
                    results_scrolled = query.se.es.scroll(
                        scroll_id=scroll_id, scroll="1m"
                    )
                    results["hits"]["hits"] += results_scrolled["hits"]["hits"]
            restricted_ids = [res["_id"] for res in results["hits"]["hits"]]
            return restricted_ids

    def update_groups_for_user(self, user: User) -> None:
        """Hook for spotting group updates on a user."""
        ...

    def update_permissions_for_user(self, user: User) -> None:
        """Hook for spotting permission updates on a user."""
        ...

    def update_permissions_for_group(self, group: Group) -> None:
        """Hook for spotting permission updates on a group."""
        ...

    def user_has_resource_model_permissions(
        self,
        user: User,
        perms: str | Iterable[str],
        resource: ResourceInstance | None = None,
        graph_id: str | None = None,
    ) -> bool:
        """
        Checks if a user has any explicit permissions to a model's nodegroups

        Arguments:
        user -- the user to check
        perms -- the permission string eg: "read_nodegroup" or list of strings
        graph_id -- a graph id to check if a user has permissions to that graph's type specifically

        """

        if resource:
            graph_id = resource.graph_id

        if graph_id is None:
            raise ValueError("graph_id must not be None to check resource permissions")

        nodegroups = self.get_nodegroups_by_perm(user, perms)
        nodes = Node.objects.filter(graph_id=graph_id).filter(nodegroup__in=nodegroups)
        return nodes.exists()

    def user_can_read_resource(
        self, user: User, resourceid: str | None = None
    ) -> bool | None:
        """
        Requires that a user be able to read an instance and read a single nodegroup of a resource

        """
        if user.is_authenticated:
            if user.is_superuser:
                return True
            if resourceid is not None and resourceid != "":
                result = self.check_resource_instance_permissions(
                    user, resourceid, "view_resourceinstance"
                )
                if result is not None:
                    if result["permitted"] == "unknown":
                        return self.user_has_resource_model_permissions(
                            user, ["models.read_nodegroup"], result["resource"]
                        )
                    else:
                        return result["permitted"]
                else:
                    return None

            return (
                len(self.get_resource_types_by_perm(user, ["models.read_nodegroup"]))
                > 0
            )
        return False

    def get_resource_types_by_perm(
        self, user: User, perms: str | Iterable[str]
    ) -> list[str]:
        """
        Returns list of graph ids that the user has specified permissions on
        """
        nodegroups = self.get_nodegroups_by_perm(user, perms)
        graphs = (
            Node.objects.values("graph_id")
            .filter(
                Q(nodegroup__in=nodegroups)
                & ~Q(graph_id=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
                & Q(graph__isresource=True)
            )
            .values_list("graph_id", flat=True)
        )

        return list(str(graph) for graph in graphs)

    def user_can_edit_resource(self, user: User, resourceid: str | None = None) -> bool:
        """
        Requires that a user be able to edit an instance and delete a single nodegroup of a resource

        """
        if user.is_authenticated:
            if user.is_superuser:
                return True
            if resourceid is not None and resourceid != "":
                result = self.check_resource_instance_permissions(
                    user, resourceid, "change_resourceinstance"
                )
                if result is not None:
                    if result["permitted"] == "unknown":
                        return user.groups.filter(
                            name__in=settings.RESOURCE_EDITOR_GROUPS
                        ).exists() or self.user_can_edit_model_nodegroups(
                            user, result["resource"]
                        )
                    else:
                        return result["permitted"]
                else:
                    return None

            return (
                user.groups.filter(name__in=settings.RESOURCE_EDITOR_GROUPS).exists()
                or len(self.get_editable_resource_types(user)) > 0
            )
        return False

    def user_can_delete_resource(
        self, user: User, resourceid: str | None = None
    ) -> bool | None:
        """
        Requires that a user be permitted to delete an instance

        """
        if user.is_authenticated:
            if user.is_superuser:
                return True
            if resourceid is not None and resourceid != "":
                result = self.check_resource_instance_permissions(
                    user, resourceid, "delete_resourceinstance"
                )
                if result is not None:
                    if result["permitted"] == "unknown":
                        nodegroups = self.get_nodegroups_by_perm(
                            user, "models.delete_nodegroup"
                        )
                        tiles = TileModel.objects.filter(resourceinstance_id=resourceid)
                        protected_tiles = {tile.nodegroup_id for tile in tiles} - set(
                            nodegroups
                        )
                        if len(protected_tiles) > 0:
                            return False
                        return user.groups.filter(
                            name__in=settings.RESOURCE_EDITOR_GROUPS
                        ).exists() or self.user_can_delete_model_nodegroups(
                            user, result["resource"]
                        )
                    else:
                        return result["permitted"]
                else:
                    return None
        return False

    def get_editable_resource_types(self, user: User) -> list[str]:
        """
        returns a list of graphs of which a user can edit resource instances

        Arguments:
        user -- the user to check

        """

        if self.user_is_resource_editor(user):
            return self.get_resource_types_by_perm(
                user, ["models.write_nodegroup", "models.delete_nodegroup"]
            )
        else:
            return []

    def get_createable_resource_types(self, user: User) -> list[str]:
        """
        returns a list of graphs of which a user can create resource instances

        Arguments:
        user -- the user to check

        """
        if self.user_is_resource_editor(user):
            return self.get_resource_types_by_perm(user, "models.write_nodegroup")
        else:
            return []

    def user_can_edit_model_nodegroups(
        self, user: User, resource: ResourceInstance
    ) -> bool:
        """
        returns a list of graphs of which a user can edit resource instances

        Arguments:
        user -- the user to check
        resource -- an instance of a model

        """

        return self.user_has_resource_model_permissions(
            user, ["models.write_nodegroup"], resource
        )

    def user_can_delete_model_nodegroups(
        self, user: User, resource: ResourceInstance
    ) -> bool:
        """
        returns a list of graphs of which a user can edit resource instances

        Arguments:
        user -- the user to check
        resource -- an instance of a model

        """

        return self.user_has_resource_model_permissions(
            user, ["models.delete_nodegroup"], resource
        )

    def user_can_read_graph(self, user: User, graph_id: str) -> bool:
        """
        returns a boolean denoting if a user has permmission to read a model's nodegroups

        Arguments:
        user -- the user to check
        graph_id -- a graph id to check if a user has permissions to that graph's type specifically

        """

        return self.user_has_resource_model_permissions(
            user, ["models.read_nodegroup"], graph_id=graph_id
        )

    def user_can_read_concepts(self, user: User) -> bool:
        """
        Requires that a user is a part of the RDM Administrator group

        """

        if user.is_authenticated:
            return user.groups.filter(name="RDM Administrator").exists()
        return False

    def user_is_resource_editor(self, user: User) -> bool:
        """
        Single test for whether a user is in the Resource Editor group
        """

        return user.groups.filter(name="Resource Editor").exists()

    def user_is_resource_reviewer(self, user: User) -> bool:
        """
        Single test for whether a user is in the Resource Reviewer group
        """

        return user.groups.filter(name="Resource Reviewer").exists()

    def user_is_resource_exporter(self, user: User) -> bool:
        """
        Single test for whether a user is in the Resource Exporter group
        """

        return user.groups.filter(name="Resource Exporter").exists()

    def user_in_group_by_name(self, user: User, names: Iterable[str]) -> bool:
        return bool(user.groups.filter(name__in=names))

    def group_required(self, user: User, *group_names: list[str]) -> bool:
        # To fully reimplement this without Django groups, the following group names must (currently) be handled:
        #  - Application Administrator
        #  - RDM Administrator
        #  - Graph Editor
        #  - Resource Editor
        #  - Resource Exporter
        #  - System Administrator

        if user.is_authenticated:
            if user.is_superuser or bool(user.groups.filter(name__in=group_names)):
                return True
        return False

    def get_default_permissions(
        self,
        user_or_group: User | Group = None,
        resource_instance: ResourceInstance = None,
        all_permissions: bool = False,
        cls: str | Model = None,
    ) -> list[str]:
        """
        Gets default permissions (if any) for a resource instance.
        """
        default_permissions_settings = settings.PERMISSION_DEFAULTS
        if not default_permissions_settings or resource_instance is None:
            return []

        default_permissions_for_graph = (
            default_permissions_settings[str(resource_instance.graph_id)]
            if str(resource_instance.graph_id) in default_permissions_settings
            else None
        )

        if default_permissions_for_graph is None:
            return []

        user_ids = []
        group_ids = []

        if isinstance(user_or_group, Group):
            group_ids.append(user_or_group.id)
        elif isinstance(user_or_group, User):
            user_ids.append(user_or_group.id)
            if all_permissions:
                group_ids = [x.id for x in user_or_group.groups.all()]
        default_permissions = [
            item
            for sub_list in [
                x["permissions"]
                for x in default_permissions_for_graph
                if (x["type"] == "user" and x["id"] in user_ids)
                or (x["type"] == "group" and x["id"] in group_ids)
            ]
            for item in sub_list
        ]
        return default_permissions

    def get_default_permissions_objects(
        self,
        user_or_group: User | Group = None,
        resource_instance: ResourceInstance = None,
        cls: str | Model = None,
    ) -> QuerySet[Permission]:
        default_permissions = self.get_default_permissions(
            user_or_group, resource_instance, cls
        )
        permissions = Permission.objects.filter(codename__in=default_permissions)
        return permissions


class PermissionBackend(ObjectPermissionBackend):  # type: ignore
    def has_perm(self, user_obj: User, perm: str, obj: Model | None = None) -> bool:
        if isinstance(obj, NodeGroup):
            # check if user_obj and object are supported (pulled directly from guardian)
            support, user_obj = check_support(user_obj, obj)
            if not support:
                return False

            if "." in perm:
                app_label, perm = perm.split(".")
                if app_label != obj._meta.app_label:
                    raise WrongAppError(
                        "Passed perm has app label of '%s' and "
                        "given obj has '%s'" % (app_label, obj._meta.app_label)
                    )

            obj_checker: ObjectPermissionChecker = CachedObjectPermissionChecker(
                user_obj, obj
            )
            explicitly_defined_perms = obj_checker.get_perms(obj)

            if len(explicitly_defined_perms) > 0:
                if "no_access_to_nodegroup" in explicitly_defined_perms:
                    return False
                else:
                    return perm in explicitly_defined_perms
            else:
                user_checker = CachedUserPermissionChecker(user_obj)
                return user_checker.user_has_permission(perm)
        return super().has_perm(user_obj, perm, obj)


class CachedUserPermissionChecker:
    """
    A permission checker that leverages the 'user_permission' cache to check user-level user permissions.
    """

    def __init__(self, user: User):
        user_permission_cache = caches["user_permission"]
        current_user_cached_permissions = user_permission_cache.get(str(user.pk), {})

        if current_user_cached_permissions.get("user_permissions"):
            user_permissions = current_user_cached_permissions.get("user_permissions")
        else:
            user_permissions = set()

            for group in user.groups.prefetch_related("permissions").all():
                for group_permission in group.permissions.all():
                    user_permissions.add(group_permission.codename)

            for user_permission in user.user_permissions.all():
                user_permissions.add(user_permission.codename)

            current_user_cached_permissions["user_permissions"] = user_permissions
            user_permission_cache.set(str(user.pk), current_user_cached_permissions)

        self.user_permissions: set[str] = user_permissions

    def user_has_permission(self, permission: str) -> bool:
        if permission in self.user_permissions:
            return True
        else:
            return False


class CachedObjectPermissionChecker:
    """
    A permission checker that leverages the 'user_permission' cache to check object-level user permissions.
    """

    def __new__(cls, user: User, input: type | Model | str) -> ObjectPermissionChecker:
        if inspect.isclass(input):
            classname = input.__name__
        elif isinstance(input, Model):
            classname = input.__class__.__name__
        elif isinstance(input, str) and globals().get(input):
            classname = input
        else:
            raise Exception("Cannot derive model from input.")

        user_permission_cache = caches["user_permission"]

        key = f"g:{user.pk}" if isinstance(user, Group) else str(user.pk)
        current_user_cached_permissions = user_permission_cache.get(key, {})

        if current_user_cached_permissions.get(classname):
            checker = current_user_cached_permissions.get(classname)
        else:
            checker = ObjectPermissionChecker(user)
            checker.prefetch_perms(globals()[classname].objects.all())

            current_user_cached_permissions[classname] = checker
            user_permission_cache.set(key, current_user_cached_permissions)

        return checker


def get_nodegroups_by_perm_for_user_or_group(
    user_or_group: User | Group,
    perms: str | Iterable[str] | None = None,
    any_perm: bool = True,
    ignore_perms: bool = False,
) -> dict[NodeGroup, set[Permission]]:
    formatted_perms = []
    if perms is None:
        if not ignore_perms:
            raise RuntimeError("Must provide perms or explicitly ignore")
    else:
        if isinstance(perms, str):
            perms = [perms]

        # in some cases, `perms` can have a `models.` prefix
        for perm in perms:
            if len(perm.split(".")) > 1:
                formatted_perms.append(perm.split(".")[1])
            else:
                formatted_perms.append(perm)

    permitted_nodegroups = {}
    checker: ObjectPermissionChecker = CachedObjectPermissionChecker(
        user_or_group,
        NodeGroup,
    )

    for nodegroup in NodeGroup.objects.all():
        explicit_perms = checker.get_perms(nodegroup)

        if len(explicit_perms):
            if ignore_perms:
                permitted_nodegroups[nodegroup] = explicit_perms
            elif any_perm:
                if len(set(formatted_perms) & set(explicit_perms)):
                    permitted_nodegroups[nodegroup] = explicit_perms
            else:
                if set(formatted_perms) == set(explicit_perms):
                    permitted_nodegroups[nodegroup] = explicit_perms
        else:  # if no explicit permissions, object is considered accessible by all with group permissions
            permitted_nodegroups[nodegroup] = set()

    return permitted_nodegroups
