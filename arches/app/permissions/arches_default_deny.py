from arches.app.permissions.arches_standard import ArchesStandardPermissionFramework

class ArchesDefaultDenyPermissionFramework(ArchesStandardPermissionFramework):
    def check_resource_instance_permissions(self, user, resourceid, permission):
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
                user_permissions = get_user_perms(user, resource)
                if "no_access_to_resourceinstance" not in user_permissions:
                    group_permissions = get_group_perms(user, resource)

                    # This should correspond to the exact case we wish to flip.
                    if permission in group_permissions and len(group_permissions) > 1:
                        result["permitted"] = True

        return result
