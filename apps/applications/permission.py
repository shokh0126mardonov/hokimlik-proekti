from rest_framework.permissions import BasePermission


class AplicationPermission(BasePermission):
    message = 'aplicationga kirishingiz mumkin emas!'

    def has_permission(self, request, view):
        return request.user and (
            request.user.super_admin or request.user.hokim or request.user.service_staff or request.user.oqsoqol
        )
    

class AplicationCreatePermission(BasePermission):
    message = 'aplicationga yaratishingiz mumkin emas!'

    def has_permission(self, request, view):
        return request.user and (
            request.user.super_admin or  request.user.service_staff
        )
    

class AplicationsSendMahallaPermissions(BasePermission):
    message = 'siz aplication send qila olmaysiz!'

    def has_permission(self, request, view):
        return request.user and (
            request.user.super_admin or  request.user.hokim
        )