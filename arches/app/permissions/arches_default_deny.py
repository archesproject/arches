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
from arches.app.models.resource import Resource
from django.contrib.auth.models import User
from arches.app.models.models import ResourceInstance

from arches.app.permissions.arches_standard import (
    ArchesStandardPermissionFramework,
    ResourceInstancePermissions,
)
from arches.app.search.elasticsearch_dsl_builder import Bool, Nested, Terms


class ArchesDefaultDenyPermissionFramework(ArchesStandardPermissionFramework):
    def get_sets_for_user(self, user: User, perm: str) -> set[str] | None:
        # We do not do set filtering - None is allow-all for sets.
        return None if user and user.username != "anonymous" else set()

    def get_restricted_users(self, resource: ResourceInstance) -> dict[str, list[int]]:
        """Fetches _explicitly_ restricted users."""
        return super().get_restricted_users(resource)

    def check_resource_instance_permissions(
        self, user: User, resourceid: str, permission: str
    ) -> ResourceInstancePermissions:
        result = super().check_resource_instance_permissions(
            user, resourceid, permission
        )

        if result and result.get("permitted", None) is not None:
            # This is a safety check - we don't want an unpermissioned user
            # defaulting to having access (allowing anonymous users is still
            # possible by assigning appropriate group permissions).
            if result["permitted"] == "unknown":
                result["permitted"] = False
            elif result["permitted"] is False:
                # This covers the case where one group denies permission and another
                # allows it. Ideally, the deny would override (as normal in Arches) but
                # this prevents us from having a default deny rule that another group
                # can override (as deny rules in Arches must be explicit for a resource).
                resource = ResourceInstance.objects.get(resourceinstanceid=resourceid)
                user_permissions = self.get_user_perms(user, resource)
                if "no_access_to_resourceinstance" not in user_permissions:
                    group_permissions = self.get_group_perms(user, resource)

                    # This should correspond to the exact case we wish to flip.
                    if permission in group_permissions:
                        result["permitted"] = True

        return result

    def process_new_user(self, instance: User, created: bool) -> None:
        pass

    def update_mappings(self):
        mappings = {}
        mappings["groups_read"] = {"type": "integer"}
        mappings["groups_edit"] = {"type": "integer"}
        mappings["users_read"] = {"type": "integer"}
        mappings["users_edit"] = {"type": "integer"}
        return mappings

    def get_index_values(self, resource: Resource):
        permissions = {}
        group_read_allowances = [
            group.id
            for group in self.get_groups_for_object("view_resourceinstance", resource)
        ]
        permissions["groups_read"] = group_read_allowances
        group_edit_allowances = [
            group.id
            for group in self.get_groups_for_object("change_resourceinstance", resource)
        ]
        permissions["groups_edit"] = group_edit_allowances
        users_read_allowances = [
            user.id
            for user in self.get_users_for_object("view_resourceinstance", resource)
        ]
        permissions["users_read"] = users_read_allowances
        users_edit_allowances = [
            user.id
            for user in self.get_users_for_object("change_resourceinstance", resource)
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

        nested_group_term_filter = Nested(path="permissions", query=group_read)
        nested_user_term_filter = Nested(path="permissions", query=user_read)
        should_access.should(nested_group_term_filter)
        should_access.should(nested_user_term_filter)
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
        result["can_read"] = user.is_superuser or (
            "permissions" in search_result["_source"]
            and "groups_read" in search_result["_source"]["permissions"]
            and (
                set(
                    search_result["_source"]["permissions"]["groups_read"]
                ).intersection(set(groups))
            )
            and user_can_read
        )

        user_can_edit = len(self.get_editable_resource_types(user)) > 0
        result["can_edit"] = user.is_superuser or (
            "permissions" in search_result["_source"]
            and "groups_edit" in search_result["_source"]["permissions"]
            and set(
                search_result["_source"]["permissions"]["groups_edit"]
            ).intersection(set(groups))
            and user_can_edit
        )

        result["is_principal"] = (
            "permissions" in search_result["_source"]
            and "principal_user" in search_result["_source"]["permissions"]
            and user.id in search_result["_source"]["permissions"]["principal_user"]
        )

        return result
