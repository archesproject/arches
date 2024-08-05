from __future__ import annotations
import sys
import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from arches.app.models.models import ResourceInstance
from arches.app.permissions.arches_permission_base import ArchesPermissionBase
from django.contrib.contenttypes.models import ContentType
from guardian.models import GroupObjectPermission
from arches.app.models.resource import Resource
from arches.app.search.elasticsearch_dsl_builder import Bool, Query, Terms, Nested
from arches.app.permissions.arches_permission_base import (
    ResourceInstancePermissions,
)
from arches.app.models.system_settings import settings
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


class ArchesDefaultAllowPermissionFramework(ArchesPermissionBase):
    def process_new_user(self, instance: User, created: bool) -> None:
        ct = ContentType.objects.get(app_label="models", model="resourceinstance")
        resourceInstanceIds = list(
            GroupObjectPermission.objects.filter(content_type=ct)
            .values_list("object_pk", flat=True)
            .distinct()
        )
        for resourceInstanceId in resourceInstanceIds:
            resourceInstanceId = uuid.UUID(resourceInstanceId)
        resources = ResourceInstance.objects.filter(pk__in=resourceInstanceIds)
        self.assign_perm("no_access_to_resourceinstance", instance, resources)
        for resource_instance in resources:
            resource = Resource(resource_instance.resourceinstanceid)  # type: ignore
            resource.graph_id = resource_instance.graph_id
            resource.createdtime = resource_instance.createdtime
            resource.index()  # type: ignore

    def get_search_ui_permissions(
        self, user: User, search_result: dict, groups
    ) -> dict:
        result = {}
        user_read_permissions = self.get_resource_types_by_perm(
            user,
            [
                "models.write_nodegroup",
                "models.delete_nodegroup",
                "models.read_nodegroup",
            ],
        )
        user_can_read = len(user_read_permissions) > 0
        result["can_read"] = (
            "permissions" in search_result["_source"]
            and "users_without_read_perm" in search_result["_source"]["permissions"]
            and (
                user.id
                not in search_result["_source"]["permissions"][
                    "users_without_read_perm"
                ]
            )
        ) and user_can_read

        user_can_edit = len(self.get_editable_resource_types(user)) > 0
        result["can_edit"] = (
            "permissions" in search_result["_source"]
            and "users_without_edit_perm" in search_result["_source"]["permissions"]
            and (
                user.id
                not in search_result["_source"]["permissions"][
                    "users_without_edit_perm"
                ]
            )
            and user_can_edit
        )
        result["is_principal"] = (
            "permissions" in search_result["_source"]
            and "principal_user" in search_result["_source"]["permissions"]
            and user.id in search_result["_source"]["permissions"]["principal_user"]
        )
        return result

    def get_sets_for_user(self, user: User, perm: str) -> set[str] | None:
        # We do not do set filtering - None is allow-all for sets.
        return None

    def get_restricted_users(self, resource: ResourceInstance) -> dict[str, list[int]]:
        """
        Takes a resource instance and identifies which users are explicitly restricted from
        reading, editing, deleting, or accessing it.

        """

        user_perms = get_users_with_perms(
            resource, attach_perms=True, with_group_users=False
        )
        user_and_group_perms = get_users_with_perms(
            resource, attach_perms=True, with_group_users=True
        )

        result: dict[str, list[int]] = {
            "no_access": [],
            "cannot_read": [],
            "cannot_write": [],
            "cannot_delete": [],
        }

        for user, perms in user_and_group_perms.items():
            if user.is_superuser:
                pass
            elif (
                user in user_perms
                and "no_access_to_resourceinstance" in user_perms[user]
            ):
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

    def check_resource_instance_permissions(
        self, user: User, resourceid: str, permission: str
    ) -> ResourceInstancePermissions:
        """
        Checks if a user has permission to access a resource instance

        Arguments:
        user -- the user to check
        resourceid -- the id of the resource
        permission -- the permission codename (e.g. 'view_resourceinstance') for which to check

        """
        result = ResourceInstancePermissions()
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
                if (
                    "no_access_to_resourceinstance" in user_permissions
                ):  # user is restricted
                    result["permitted"] = False
                    return result
                elif permission in user_permissions:  # user is permitted
                    result["permitted"] = True
                    return result

                group_permissions = self.get_group_perms(user, resource)
                if (
                    "no_access_to_resourceinstance" in group_permissions
                ):  # group is restricted - no user override
                    result["permitted"] = False
                    return result
                elif (
                    permission in group_permissions
                ):  # group is permitted - no user override
                    result["permitted"] = True
                    return result

                if (
                    permission not in all_perms
                ):  # neither user nor group explicitly permits or restricts.
                    result["permitted"] = False  # restriction implied
                    return result

        except ObjectDoesNotExist:
            result["permitted"] = (
                True  # if the object does not exist, should return true - this prevents strange 403s.
            )
            return result

    def update_mappings(self):
        mappings = {}
        mappings["users_without_read_perm"] = {"type": "integer"}
        mappings["users_without_edit_perm"] = {"type": "integer"}
        mappings["users_without_delete_perm"] = {"type": "integer"}
        mappings["users_with_no_access"] = {"type": "integer"}
        return mappings

    def get_index_values(self, resource: Resource):
        restrictions = self.get_restricted_users(resource)
        permissions = {}
        permissions["users_without_read_perm"] = restrictions["cannot_read"]
        permissions["users_without_edit_perm"] = restrictions["cannot_write"]
        permissions["users_without_delete_perm"] = restrictions["cannot_delete"]
        permissions["users_with_no_access"] = restrictions["no_access"]
        return permissions

    def get_permission_inclusions(self) -> list:
        return [
            "permissions.users_without_read_perm",
            "permissions.users_without_edit_perm",
            "permissions.users_without_delete_perm",
            "permissions.users_with_no_access",
            "permissions.principal_user",
        ]

    def get_permission_search_filter(self, user: User) -> Bool:
        has_access = Bool()
        terms = Terms(field="permissions.users_with_no_access", terms=[str(user.id)])
        nested_term_filter = Nested(path="permissions", query=terms)
        has_access.must_not(nested_term_filter)
        return has_access

    def has_group_perm(self, group, perm, obj):
        explicitly_defined_perms = self.get_perms(group, obj)
        if len(explicitly_defined_perms) > 0:
            if "no_access_to_nodegroup" in explicitly_defined_perms:
                return False
            else:
                return perm in explicitly_defined_perms
        else:
            for permission in group.permissions.all():
                if perm in permission.codename:
                    return True
            return False
