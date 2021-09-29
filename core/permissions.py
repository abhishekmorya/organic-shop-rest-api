from rest_framework import permissions


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    The request is authenticates as staff, or it is a read only request
    """

    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS or
            request.user and
            request.user.is_authenticated and
            request.user.is_staff
        )