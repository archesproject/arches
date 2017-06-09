from guardian.backends import check_support
from guardian.backends import ObjectPermissionBackend
from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import get_user_perms, get_users_with_perms
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

class PermissionChecker(object):
    def get_groups_for_object(self, perm, obj):
        """
        get's a list of object level permissions allowed for a all groups

        returns an object of the form:
        .. code-block:: python
            {
                'local':  {'codename': permssion codename, 'name': permission name} # A list of object level permissions
                'default': {'codename': permssion codename, 'name': permission name} # A list of model level permissions
            }

        Keyword Arguments:
        nodegroup -- the NodeGroup object instance to use to check for permissions on that particular object

        """

        ret = []
        for group in Group.objects.all():
            for permission in group.permissions.all():
                    if perm in permission.codename:
                        ret.append(group.name)
        return sorted(ret)

    def get_users_for_object(self, perm, obj):
        """
        get's a list of object level permissions allowed for a all users

        returns an object of the form:
        .. code-block:: python
            {
                'local':  {'codename': permssion codename, 'name': permission name} # A list of object level permissions
                'default': {'codename': permssion codename, 'name': permission name} # A list of group based object level permissions or model level permissions
            }

        Keyword Arguments:
        nodegroup -- the NodeGroup object instance to use to check for permissions on that particular object

        """

        ret = []
        for user in User.objects.all():
            if user.has_perm(perm, obj):
                ret.append(user.email or user.username)
        return sorted(ret)
