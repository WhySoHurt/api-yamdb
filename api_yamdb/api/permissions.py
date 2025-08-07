from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(IsAdmin):
    """Чтение - всем, запись - только админу."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or super().has_permission(request, view)
        )


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    """
    Разрешает доступ, если пользователь - автор объекта,
    или имеет роль модератора или администратора.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        return request.method in permissions.SAFE_METHODS or (
            user.is_authenticated
            and (obj.author == user or user.is_admin or user.is_moderator)
        )
