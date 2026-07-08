from rest_framework.permissions import BasePermission


class Is_SuperAdmin(BasePermission):
    message = "Siz super admin emassiz"

    def has_permission(self, request, view):
        return request.user and request.user.super_admin
