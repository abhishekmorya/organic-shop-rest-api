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


class IsStaffOrAuthenticated(permissions.IsAuthenticated):
    """
    The request is authenticated as staff, or it is read only for normal users
    Restricted for anonymous users
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.method in permissions.SAFE_METHODS or request.user.is_staff)
        )