from rest_framework import permissions


class IsAdminModeratorOrAuthor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            request.user.role in ('admin', 'moderator')
            or request.user.is_staff
            or obj.author == request.user
        )


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and (
                request.user.is_staff or request.user.role == 'admin'
            )
        )
