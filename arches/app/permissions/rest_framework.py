from rest_framework import permissions

from arches.app.utils.permission_backend import group_required


class RDMAdministrator(permissions.BasePermission):
    def has_permission(self, request, view):
        return group_required(request.user, "RDM Administrator")
