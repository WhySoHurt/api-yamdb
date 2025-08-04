from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, filters
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)

from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Title, Review, Comment
from .filters import TitleFilter
from .permissions import IsAdminOrReadOnly, IsAdmin, IsAuthorOrModeratorOrAdmin
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    TitleCreateSerializer,
    ReviewSerializer,
    CommentSerializer,
    SignUpSerializer,
    TokenSerializer,
    UserSerializer,
)

from reviews.constants import EDIT_ENDPOINT


User = get_user_model()


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['name']
    search_fields = ['name']
    permission_classes = [IsAdminOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['name']
    search_fields = ['name']
    permission_classes = [IsAdminOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('id')
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter
    permission_classes = [IsAdminOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleSerializer
        return TitleCreateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для запросов к отзывам."""

    serializer_class = ReviewSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [
        IsAuthenticatedOrReadOnly, IsAuthorOrModeratorOrAdmin]

    def get_title(self):
        """Возвращает произведение по pk, указанному в URL."""
        return get_object_or_404(Title, pk=self.kwargs['title_pk'])

    def get_queryset(self):
        """Возвращает отзыв к произведению."""
        return Review.objects.filter(title=self.get_title())

    def perform_create(self, serializer):
        """Сохраняет отзыв, подставляя автора и произведение."""
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для запросов к комментариям."""

    serializer_class = CommentSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [
        IsAuthenticatedOrReadOnly, IsAuthorOrModeratorOrAdmin]

    def get_review(self):
        """Возвращает отзыв по pk, указанному в URL."""
        return get_object_or_404(Review, pk=self.kwargs['review_pk'])

    def get_queryset(self):
        """Возвращает комментарий к отзыву."""
        return Comment.objects.filter(review=self.get_review())

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
    user, created = User.objects.get_or_create(
        username=username,
        email=email,
        defaults={'username': username, 'email': email},
    )
    if username in user.username:
        if user.email != email:
            raise ValidationError(
                {'email': 'Email не соответствует существующему пользователю'},
            )
        user.confirmation_code = get_random_string(length=20)
        user.save()
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
        serializer = self.get_serializer(
            user, data=request.data, partial=True
        )

        serializer.is_valid(raise_exception=True)
        if not user.is_admin:
            serializer.save(role=user.role)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
