from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    DestroyModelMixin
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from reviews.constants import (
    CONFIRMATION_CODE_CHARS,
    CONFIRMATION_CODE_LENGTH,
    EDIT_ENDPOINT,
)
from reviews.models import Category, Genre, Review, Title

from .filters import TitleFilter
from .permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrModeratorOrAdmin
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    TokenSerializer,
    UserSerializer,
)

User = get_user_model()


class BaseCategoryGenreViewSet(
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Базовый вьюсет для категорий и жанров."""

    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['name']
    search_fields = ['name']
    permission_classes = [IsAdminOrReadOnly]


class CategoryViewSet(BaseCategoryGenreViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(BaseCategoryGenreViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by(*Title._meta.ordering)
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter
    permission_classes = [IsAdminOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для запросов к отзывам."""

    serializer_class = ReviewSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdmin,
    ]

    def get_title(self):
        """Возвращает произведение по pk, указанному в URL."""
        return get_object_or_404(Title, pk=self.kwargs['title_pk'])

    def get_queryset(self):
        """Возвращает отзыв к произведению."""
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        """Сохраняет отзыв, подставляя автора и произведение."""
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для запросов к комментариям."""

    serializer_class = CommentSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdmin,
    ]

    def get_review(self):
        """Возвращает отзыв по pk, указанному в URL."""
        return get_object_or_404(Review, pk=self.kwargs['review_pk'])

    def get_queryset(self):
        """Возвращает комментарий к отзыву."""
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        """Сохраняет комментарий, подставляя автора и отзыв."""
        serializer.save(author=self.request.user, review=self.get_review())


@api_view(('POST',))
@permission_classes([AllowAny])
def token_view(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    confirmation_code = serializer.validated_data['confirmation_code']

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise NotFound('Пользователь не найден')
    if user.confirmation_code != confirmation_code:
        return Response(
            {'confirmation_code': 'Неверный код'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    token = AccessToken.for_user(user)
    return Response({'token': str(token)}, status=status.HTTP_200_OK)


@api_view(('POST',))
@permission_classes([AllowAny])
def signup_view(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    email = serializer.validated_data['email']
    confirmation_code = get_random_string(
        length=CONFIRMATION_CODE_LENGTH,
        allowed_chars=CONFIRMATION_CODE_CHARS,
    )
    try:
        user, created = User.objects.get_or_create(
            username=username,
            email=email,
            defaults={'confirmation_code': confirmation_code},
        )
        if not created:
            user.confirmation_code = confirmation_code
            user.save()

    except IntegrityError as e:
        error_msg = str(e)
        if 'username' in error_msg:
            raise ValidationError(
                {'username': 'Пользователь с таким username уже существует.'}
            )
        elif 'email' in error_msg:
            raise ValidationError(
                {'email': 'Пользователь с таким email уже существует.'}
            )
    send_mail(
        'Код подтверждения',
        f'Ваш код: {user.confirmation_code}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=True,
    )

    return Response(
        {'email': email, 'username': username}, status=status.HTTP_200_OK
    )


class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(
        detail=False,
        methods=['get', 'post', 'patch'],
        permission_classes=[IsAuthenticated],
        url_path=EDIT_ENDPOINT,
    )
    def edit_profile(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        serializer = self.get_serializer(user, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
