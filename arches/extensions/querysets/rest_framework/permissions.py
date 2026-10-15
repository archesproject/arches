from rest_framework import permissions

from arches.app.utils.permission_backend import group_required


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class Guest(permissions.BasePermission):
    def has_permission(self, request, view):
        return group_required(request.user, "Guest")


class RDMAdministrator(permissions.BasePermission):
    def has_permission(self, request, view):
        return group_required(request.user, "RDM Administrator")


class ResourceEditor(permissions.BasePermission):
    def has_permission(self, request, view):
        return group_required(request.user, "Resource Editor")
