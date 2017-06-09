from guardian.backends import check_support
from guardian.backends import ObjectPermissionBackend
from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import get_perms
from guardian.exceptions import WrongAppError
from django.contrib.auth.models import User, Group, Permission

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

        explicitly_defined_perms = get_perms(user_obj, obj)
        if len(explicitly_defined_perms) > 0:
            if 'no_access_to_nodegroup' in explicitly_defined_perms:
                return False
            else:
                return perm in explicitly_defined_perms
        else:
            default_perms = []
            for group in user_obj.groups.all():
                for permission in group.permissions.all():
                    if perm in permission.codename:
                        return True
            return False


def get_groups_for_object(perm, obj):
    """
    returns a list of group objects that have the given permission on the given object

    Arguments:
    perm -- the permssion string eg: "read_nodegroup"
    obj -- the model instance to check

    """

    def has_group_perm(group, perm, obj):
        explicitly_defined_perms = get_perms(group, obj)
        if len(explicitly_defined_perms) > 0:
            if 'no_access_to_nodegroup' in explicitly_defined_perms:
                return False
            else:
                return perm in explicitly_defined_perms
        else:
            default_perms = []
            for permission in group.permissions.all():
                if perm in permission.codename:
                    return True
            return False

    ret = []
    for group in Group.objects.all():
        if has_group_perm(group, perm, obj):
            ret.append(group)
    return ret

def get_users_for_object(perm, obj):
    """
    returns a list of user objects that have the given permission on the given object

    Arguments:
    perm -- the permssion string eg: "read_nodegroup"
    obj -- the model instance to check

    """

    ret = []
    for user in User.objects.all():
        if user.has_perm(perm, obj):
            ret.append(user)
    return ret
