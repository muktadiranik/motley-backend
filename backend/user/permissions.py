from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.permissions import SAFE_METHODS


class IsAdminOrReadOnly(IsAuthenticatedOrReadOnly):
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated and
            request.user.is_staff
        )


class IsAdminOrStaffOrNewUser(IsAdminUser):
    METHODS = ('POST', 'HEAD', 'OPTIONS')

    def has_permission(self, request, view):
        return bool(
            request.method in self.METHODS or
            request.user.is_authenticated and
            request.user.is_staff
        )
