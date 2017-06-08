from guardian.backends import ObjectPermissionBackend
from guardian.shortcuts import get_user_perms

class PermissionBackend(ObjectPermissionBackend):
    def has_perm(self, user_obj, perm, obj=None):
        user_defined_perms = get_user_perms(user_obj, obj)
        if len(user_defined_perms) > 0:
            if 'no_access_to_nodegroup' in user_defined_perms:
                return False
            else:
                return perm in user_defined_perms
        else:
            default_perms = []
            for group in user_obj.groups.all():
                for permission in group.permissions.all():
                    if perm in permission.codename:
                        return True
            return False