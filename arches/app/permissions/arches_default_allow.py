import logging
import uuid

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from guardian.models import GroupObjectPermission, UserObjectPermission

from arches.app.models.models import ResourceInstance
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
from arches.app.permissions.arches_permission_base import (
    ArchesPermissionBase,
    ResourceInstancePermissions,
)
from arches.app.search.elasticsearch_dsl_builder import Bool, Ids, Terms, Nested, Query
from arches.app.search.mappings import RESOURCES_INDEX
from arches.app.search.search import SearchEngine


logger = logging.getLogger(__name__)


class ArchesDefaultAllowPermissionFramework(ArchesPermissionBase):
    is_exclusive = False

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
        """
        Determintes whether or not read/edit buttons show up in search results.
        """
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

        # validate permissions structure for search result
        deny_read_exists = (
            "permissions" in search_result["_source"]
            and "users_without_read_perm" in search_result["_source"]["permissions"]
        )
        deny_edit_exists = (
            "permissions" in search_result["_source"]
            and "users_without_edit_perm" in search_result["_source"]["permissions"]
        )

        if not deny_read_exists or not deny_edit_exists:
            logger.warning(
                """
                PROBLEM WITH INDEX - it appears that your index permissions are malformed.  
                This can happen when switching permission frameworks and may cause search 
                results to appear incorrectly or with invalid permissions.  You can correct it by reindexing arches.
                """
            )

        result["can_read"] = (
            deny_read_exists
            and (
                user.id
                not in search_result["_source"]["permissions"][
                    "users_without_read_perm"
                ]
            )
        ) and user_can_read

        user_can_edit = len(self.get_editable_resource_types(user)) > 0

        result["can_edit"] = (
            deny_edit_exists
            and (
                user.id
                not in search_result["_source"]["permissions"][
                    "users_without_edit_perm"
                ]
            )
        ) and user_can_edit

        result["is_principal"] = (
            "permissions" in search_result["_source"]
            and "principal_user" in search_result["_source"]["permissions"]
            and user.id in search_result["_source"]["permissions"]["principal_user"]
        )
        return result

    def get_sets_for_user(self, user: User, perm: str) -> set[str] | None:
        # We do not do set filtering - None is allow-all for sets.
        return None

    def get_restricted_users(self, resource: ResourceInstance) -> dict[str, set[int]]:
        """
        Takes a resource instance and identifies which users are explicitly restricted from
        reading, editing, deleting, or accessing it.

        """

        user_perms = self.get_users_with_perms(
            resource, attach_perms=True, with_group_users=False
        )
        user_and_group_perms = self.get_users_with_perms(
            resource, attach_perms=True, with_group_users=True
        )

        result: dict[str, set[int]] = {
            "no_access": set(),
            "cannot_read": set(),
            "cannot_write": set(),
            "cannot_delete": set(),
        }
        for user in User.objects.all():
            default_permissions = self.get_default_permissions(
                user, resource, all_permissions=True
            )
            if (
                not (user.is_superuser)
                and resource.principaluser_id != user.id
                and "no_access_to_resourceinstance" in default_permissions
            ):
                for k, v in result.items():
                    v.add(user.id)
        for user, perms in user_and_group_perms.items():
            default_permissions = self.get_default_permissions(
                user, resource, all_permissions=True
            )
            if user.is_superuser:
                pass
            elif user in user_perms and (
                "no_access_to_resourceinstance" in user_perms[user]
            ):
                for k, v in result.items():
                    v.add(user.id)
            else:
                if "view_resourceinstance" not in perms:
                    result["cannot_read"].add(user.id)
                if "change_resourceinstance" not in perms:
                    result["cannot_write"].add(user.id)
                if "delete_resourceinstance" not in perms:
                    result["cannot_delete"].add(user.id)
                if "no_access_to_resourceinstance" in perms and len(perms) == 1:
                    result["no_access"].add(user.id)

        return result

    def get_filtered_instances(
        self,
        user: User,
        search_engine: SearchEngine | None = None,
        allresources: bool = False,
        resources: list[str] | None = None,
    ):
        allowed_instances = self.get_restricted_instances(
            user, search_engine, allresources, resources
        )

        return (self.__class__.is_exclusive, allowed_instances)

    def get_restricted_instances(
        self,
        user: User,
        search_engine: SearchEngine | None = None,
        allresources: bool = False,
        resources: list[str] = None,
    ) -> list[str]:
        if allresources is False and user.is_superuser is True:
            return []

        if allresources is True:
            group_object_permissions = GroupObjectPermission.objects.filter(
                permission__codename="no_access_to_resourceinstance"
            )
            if resources is not None:
                group_object_permissions.filter(object_pk__in=resources)

            restricted_group_instances = {
                perm["object_pk"]
                for perm in group_object_permissions.values("object_pk")
            }
            user_object_permissions = UserObjectPermission.objects.filter(
                permission__codename="no_access_to_resourceinstance"
            )
            if resources is not None:
                user_object_permissions.filter(object_pk__in=resources)

            restricted_user_instances = {
                perm["object_pk"]
                for perm in user_object_permissions.values("object_pk")
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
            if resources is not None:
                has_access.filter(
                    Ids(
                        ids=resources,
                    )
                )

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

    def check_resource_instance_permissions(
        self,
        user: User,
        resourceid: str | None,
        permission: str,
        *,
        resource: ResourceInstance | None = None,
    ) -> ResourceInstancePermissions:
        """
        Checks if a user has permission to access a resource instance

        Arguments:
        user -- the user to check
        resourceid -- the id of the resource
        permission -- the permission codename (e.g. 'view_resourceinstance') for which to check

        Optional arguments:
        resource -- provide an instance to avoid having to fetch it by ID.
        """
        result = ResourceInstancePermissions()
        try:
            if not resource:
                resource = ResourceInstance.objects.select_related(
                    "resource_instance_lifecycle_state"
                ).get(resourceinstanceid=resourceid)
            elif resourceid:
                raise ValueError("resourceid and resource are mutually incompatible")
            result["resource"] = resource

            if str(resource.pk) == settings.SYSTEM_SETTINGS_RESOURCE_ID:
                if not user.groups.filter(name="System Administrator").exists():
                    result["permitted"] = False
                    return result

            all_perms = self.get_perms(user, resource)

            if len(all_perms) == 0:  # no permissions assigned. permission implied
                result["permitted"] = "unknown"
                return result
            else:
                user_permissions = [
                    x.codename for x in self.get_user_perms(user, resource)
                ]
                if (
                    "no_access_to_resourceinstance" in user_permissions
                ):  # user is restricted
                    result["permitted"] = False
                    return result
                elif permission in user_permissions:  # user is permitted
                    result["permitted"] = True
                    return result

                group_permissions = [
                    x.codename for x in self.get_group_perms(user, resource)
                ]

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
        permissions["users_without_read_perm"] = list(restrictions["cannot_read"])
        permissions["users_without_edit_perm"] = list(restrictions["cannot_write"])
        permissions["users_without_delete_perm"] = list(restrictions["cannot_delete"])
        permissions["users_with_no_access"] = list(restrictions["no_access"])
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

    def get_default_settable_permissions(self) -> list[str]:
        """
        Get default settable permissions for a resource instance that will be displayed in the permissions designer.
        """
        return [
            "view_resourceinstance",
            "change_resourceinstance",
            "delete_resourceinstance",
            "no_access_to_resourceinstance",
        ]
