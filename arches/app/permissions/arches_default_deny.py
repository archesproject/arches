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

from django.contrib.auth.models import User

from arches.app.models.models import ResourceInstance
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
from arches.app.permissions.arches_permission_base import (
    ArchesPermissionBase,
    ResourceInstancePermissions,
)
from arches.app.search.elasticsearch_dsl_builder import Bool, Query, Terms, Nested, Ids
from arches.app.search.search import SearchEngine
from arches.app.search.mappings import RESOURCES_INDEX


class ArchesDefaultDenyPermissionFramework(ArchesPermissionBase):
    is_exclusive = True

    def get_sets_for_user(self, user: User, perm: str) -> set[str] | None:
        # We do not do set filtering - None is allow-all for sets.
        return None if user and user.username != "anonymous" else set()

    def get_restricted_users(self, resource: ResourceInstance) -> dict[str, list[int]]:
        pass

    def get_filtered_instances(
        self,
        user: User,
        search_engine: SearchEngine | None = None,
        allresources: bool = False,
        resources: list[str] | None = None,
    ):
        allowed_instances = self.get_allowed_instances(
            user, search_engine, allresources, resources
        )

        return (self.__class__.is_exclusive, allowed_instances)

    def get_allowed_instances(
        self,
        user: User,
        search_engine: SearchEngine | None = None,
        allresources: bool = False,
        resources: list[str] | None = None,
    ):
        all = False
        if user.is_superuser is True:
            if resources is not None:
                return resources
            else:
                all = True

        query = Query(search_engine, start=0, limit=settings.SEARCH_RESULT_LIMIT)  # type: ignore
        nested_groups_read = Nested(
            path="permissions",
            query=Terms(
                field="permissions.groups_read",
                terms=[str(group.id) for group in user.groups.all()],
            ),
        )

        nested_users_read = Nested(
            path="permissions",
            query=Terms(field="permissions.users_read", terms=[str(user.id)]),
        )

        if not all:
            if resources is not None:
                subset_query = Bool()
                subset_query = (
                    subset_query.filter(
                        Ids(
                            ids=resources,
                        )
                    )
                    .should(nested_users_read)
                    .should(nested_groups_read)
                )
                query.add_query(subset_query)
            else:
                query.add_query(Bool().should(nested_groups_read).should(nested_users_read))  # type: ignore

        results = query.search(index=RESOURCES_INDEX, scroll="1m")  # type: ignore
        scroll_id = results["_scroll_id"]
        total = results["hits"]["total"]["value"]
        if total > settings.SEARCH_RESULT_LIMIT:
            pages = total // settings.SEARCH_RESULT_LIMIT
            for page in range(pages):
                results_scrolled = query.se.es.scroll(scroll_id=scroll_id, scroll="1m")
                results["hits"]["hits"] += results_scrolled["hits"]["hits"]
        restricted_ids = [res["_id"] for res in results["hits"]["hits"]]
        return restricted_ids

    def check_resource_instance_permissions(
        self, user: User, resourceid: str, permission: str
    ) -> ResourceInstancePermissions:

        result = ResourceInstancePermissions()
        resource = ResourceInstance.objects.get(resourceinstanceid=resourceid)
        if resourceid == settings.SYSTEM_SETTINGS_RESOURCE_ID:
            result["resource"] = resource
            if not user.groups.filter(name="System Administrator").exists():
                result["permitted"] = False
            else:
                result["permitted"] = True
            return result

        if resource.principaluser_id == user.id:
            result["permitted"] = True
            result["resource"] = resource
            return result

        result["resource"] = resource
        result["permitted"] = False  # by default, deny

        all_perms = self.get_perms(user, resource)

        if permission in all_perms:  # user is permitted
            result["permitted"] = True

        return result

    def update_mappings(self):
        mappings = {}
        mappings["groups_read"] = {"type": "integer"}
        mappings["groups_edit"] = {"type": "integer"}
        mappings["users_read"] = {"type": "integer"}
        mappings["users_edit"] = {"type": "integer"}
        return mappings

    def has_group_perm(self, group, perm, obj):
        explicitly_defined_perms = self.get_perms(group, obj)
        if len(explicitly_defined_perms) > 0:
            return perm in explicitly_defined_perms
        else:  # for default deny, explicit permissions are required.  Model level permissions are bypassed.
            return False

    def get_index_values(self, resource: Resource):
        permissions = {}
        group_read_allowances = [
            group.id
            for group in self.get_groups_with_permission_for_object(
                "view_resourceinstance", resource
            )
        ]
        permissions["groups_read"] = group_read_allowances
        group_edit_allowances = [
            group.id
            for group in self.get_groups_with_permission_for_object(
                "change_resourceinstance", resource
            )
        ]
        permissions["groups_edit"] = group_edit_allowances
        users_read_allowances = [
            user.id
            for user in self.get_users_with_permission_for_object(
                "view_resourceinstance", resource
            )
        ]
        permissions["users_read"] = users_read_allowances
        users_edit_allowances = [
            user.id
            for user in self.get_users_with_permission_for_object(
                "change_resourceinstance", resource
            )
        ]
        permissions["users_edit"] = users_edit_allowances
        permissions["principal_user"] = [resource.principaluser_id]
        return permissions

    def get_permission_inclusions(self) -> list:
        return [
            "permissions.groups_read",
            "permissions.groups_edit",
            "permissions.users_read",
            "permissions.users_edit",
            "permissions.principal_user",
        ]

    def get_permission_search_filter(self, user: User) -> Bool:
        has_access = Bool()
        should_access = Bool()
        group_read = Terms(
            field="permissions.groups_read",
            terms=[str(group.id) for group in user.groups.all()],
        )
        user_read = Terms(field="permissions.users_read", terms=[str(user.id)])
        principal_user = Terms(field="permissions.principal_user", terms=[str(user.id)])

        nested_group_term_filter = Nested(path="permissions", query=group_read)
        nested_user_term_filter = Nested(path="permissions", query=user_read)
        principal_user_term_filter = Nested(path="permissions", query=principal_user)
        should_access.should(nested_group_term_filter)
        should_access.should(nested_user_term_filter)
        should_access.should(principal_user_term_filter)
        has_access.filter(should_access)
        return has_access

    def get_search_ui_permissions(
        self, user: User, search_result: dict, groups: list[str]
    ) -> dict:
        result = {}
        user_can_read = self.get_resource_types_by_perm(
            user,
            [
                "models.write_nodegroup",
                "models.delete_nodegroup",
                "models.read_nodegroup",
            ],
        )

        # validate permissions structure for search result
        users_read_exists = (
            "permissions" in search_result["_source"]
            and "users_read" in search_result["_source"]["permissions"]
        )
        users_edit_exists = (
            "permissions" in search_result["_source"]
            and "users_edit" in search_result["_source"]["permissions"]
        )
        groups_read_exists = (
            "permissions" in search_result["_source"]
            and "groups_read" in search_result["_source"]["permissions"]
        )
        groups_edit_exists = (
            "permissions" in search_result["_source"]
            and "groups_edit" in search_result["_source"]["permissions"]
        )
        result["can_read"] = user.is_superuser or (
            (
                groups_read_exists
                and len(
                    set(
                        search_result["_source"]["permissions"]["groups_read"]
                    ).intersection(set(groups))
                )
                > 0
            )
            or (
                users_read_exists
                and len(
                    set(
                        search_result["_source"]["permissions"]["users_read"]
                    ).intersection(set([user.id]))
                )
                > 0
            )
            and user_can_read
        )

        user_can_edit = len(self.get_editable_resource_types(user)) > 0
        result["can_edit"] = (
            user.is_superuser
            or (
                groups_edit_exists
                and len(
                    set(
                        search_result["_source"]["permissions"]["groups_edit"]
                    ).intersection(set(groups))
                )
                > 0
                and user_can_edit
            )
            or (
                users_edit_exists
                and len(
                    set(
                        search_result["_source"]["permissions"]["users_edit"]
                    ).intersection(set([user.id]))
                )
                > 0
                and user_can_edit
            )
        )

        result["is_principal"] = (
            "permissions" in search_result["_source"]
            and "principal_user" in search_result["_source"]["permissions"]
            and user.id in search_result["_source"]["permissions"]["principal_user"]
        )

        return result

    def user_can_read_resource(self, user: User, resourceid: str | None = None) -> bool:
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
                    return False

            return (
                len(self.get_resource_types_by_perm(user, ["models.read_nodegroup"]))
                > 0
            )
        return False

    def get_default_settable_permissions(self) -> list[str]:
        """
        Get default settable permissions for a resource instance that will be displayed in the permissions designer.
        """
        return [
            "view_resourceinstance",
            "change_resourceinstance",
            "delete_resourceinstance",
        ]
