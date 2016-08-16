from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from guardian.core import ObjectPermissionChecker as GuardianObjectPermissionChecker
from guardian.shortcuts import get_user_perms, get_group_perms, assign_perm

class ObjectPermissionChecker(GuardianObjectPermissionChecker):
    def get_user_perms(self, obj):
        ctype = ContentType.objects.get_for_model(obj)

        perms_qs = Permission.objects.filter(content_type=ctype)
        user_filters = self.get_user_filters(obj)
        user_perms_qs = perms_qs.filter(**user_filters)
        user_perms = user_perms_qs.values('codename', 'name')

        return user_perms

    def get_group_perms(self, obj):
        ctype = ContentType.objects.get_for_model(obj)

        perms_qs = Permission.objects.filter(content_type=ctype)
        group_filters = self.get_group_filters(obj)
        group_perms_qs = perms_qs.filter(**group_filters)
        group_perms = group_perms_qs.values('codename', 'name')

        return group_perms