from arches.app.permissions.arches_standard import ArchesStandardPermissionFramework

class ArchesAllowWithCredentialsFramework(ArchesStandardPermissionFramework):
    def get_sets_for_user(self, user, perm):
        # We do not do set filtering - None is allow-all for sets.
        return None if user and user.username != "anonymous" else set()

    def check_resource_instance_permissions(self, user, resourceid, permission):
        result = super().check_resource_instance_permissions(user, resourceid, permission)

        if result and result.get("permitted", None) is not None:
            if result["permitted"] == "unknown":
                if not user or user.username == "anonymous":
                    result["permitted"] = False
            elif result["permitted"] == False:

                # This covers the case where one group denies permission and another
                # allows it. Ideally, the deny would override (as normal in Arches) but
                # this prevents us from having a default deny rule that another group
                # can override (as deny rules in Arches must be explicit for a resource).
                resource = ResourceInstance.objects.get(resourceinstanceid=resourceid)
                user_permissions = get_user_perms(user, resource)
                if "no_access_to_resourceinstance" not in user_permissions:
                    group_permissions = get_group_perms(user, resource)

                    # This should correspond to the exact case we wish to flip.
                    if permission in group_permissions:
                        result["permitted"] = True

        return result
