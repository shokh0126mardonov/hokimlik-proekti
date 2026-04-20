from rest_framework.permissions import BasePermission


class AuditPermissions(BasePermission):
    message = "siz attachment qila olmaysiz!"

    def has_permission(self, request, view):
        return request.user and (request.user.super_admin)
