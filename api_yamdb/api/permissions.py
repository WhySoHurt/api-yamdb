from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Чтение - всем, запись - только админу."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (request.user.is_authenticated
                and (request.user.is_admin or request.user.is_superuser))


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    """
    Разрешает доступ, если пользователь - автор объекта,
    или имеет роль модератора или администратора.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if not user.is_authenticated:
            return False

        return (
            obj.author == user
            or getattr(user, 'role', None) in ['moderator', 'admin']
        )