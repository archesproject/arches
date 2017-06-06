from guardian.backends import ObjectPermissionBackend
from guardian.core import ObjectPermissionChecker

class PermissionBackend(ObjectPermissionBackend):
    def has_perm(self, user_obj, perm, obj=None):
        if (super(PermissionBackend, self).has_perm(user_obj, 'no_access_to_nodegroup', obj)):
            return False
        obj_perm = super(PermissionBackend, self).has_perm(user_obj, perm, obj)

        if obj_perm:
            return True
        else:
            default_perms = []
            for group in user_obj.groups.all():
                for permission in group.permissions.all():
                    if perm in permission.codename:
                        return True
            return False