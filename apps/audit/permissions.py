from rest_framework.permissions import BasePermission

class AuditPermissions(BasePermission):
    message = 'siz attachment qila olmaysiz!'

    def has_permission(self, request, view):
        return request.user and (
            request.user.super_admin or  request.user.service_staff or request.hokim
        )