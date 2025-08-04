from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsAdminModeratorOrAuthor


# если будет подходить, под ваши задачи, то можно переименовать
# в DefaultPermissionMixin и использовать в своих вьюсетах.
class ReviewCommentPermissionMixin:
    """
    Автоматически определяет права доступа в зависимости от запроса.
    """

    def get_permissions(self):
        """Устанавливает класс доступа в зависимости от метода запроса."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        elif self.action in ['partial_update', 'update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAdminModeratorOrAuthor]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]
