from guardian.backends import ObjectPermissionBackend
from guardian.shortcuts import get_user_perms
from guardian.backends import check_support
from guardian.exceptions import WrongAppError

class PermissionBackend(ObjectPermissionBackend):
    def has_perm(self, user_obj, perm, obj=None):
        # check if user_obj and object are supported (pulled directly from guardian)
        support, user_obj = check_support(user_obj, obj)
        if not support:
            return False

        if '.' in perm:
            app_label, perm = perm.split('.')
            if app_label != obj._meta.app_label:
                raise WrongAppError("Passed perm has app label of '%s' and "
                                    "given obj has '%s'" % (app_label, obj._meta.app_label))

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