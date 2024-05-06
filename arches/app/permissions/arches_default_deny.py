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

from arches.app.search.components.resource_type_filter import get_permitted_graphids
from django.contrib.auth.models import User
from arches.app.models.models import ResourceInstance

from arches.app.permissions.arches_standard import ArchesStandardPermissionFramework, ResourceInstancePermissions

class ArchesDefaultDenyPermissionFramework(ArchesStandardPermissionFramework):
    def get_sets_for_user(self, user: User, perm: str) -> set[str] | None:
        # We do not do set filtering - None is allow-all for sets.
        return None if user and user.username != "anonymous" else set()


    def get_restricted_users(self, resource: ResourceInstance) -> dict[str, list[int]]:
        """Fetches _explicitly_ restricted users."""
        return super().get_restricted_users(resource)


    def check_resource_instance_permissions(self, user: User, resourceid: str, permission: str) -> ResourceInstancePermissions:
        result = super().check_resource_instance_permissions(user, resourceid, permission)

        if result and result.get("permitted", None) is not None:
            # This is a safety check - we don't want an unpermissioned user
            # defaulting to having access (allowing anonymous users is still
            # possible by assigning appropriate group permissions).
            if result["permitted"] == "unknown":
                result["permitted"] = False
            elif result["permitted"] == False:

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
