from rest_framework.permissions import BasePermission

class GetMahallaPermissions(BasePermission):
    message = 'siz bu methoddan foydalana olmaysiz!'

    def has_permission(self, request, view):
        return request.user and (
            request.user.super_admin or  request.user.hokim
        )