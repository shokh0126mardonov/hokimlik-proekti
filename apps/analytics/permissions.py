from apps.accounts.models import User
from rest_framework.permissions import BasePermission


class StatisticPermissions(BasePermission):
    message = 'siz bu methoddan foydalan olmaysiz!'

    def has_permission(self, request, view):
        return request.user and (request.user.super_admin or request.user.hokim)