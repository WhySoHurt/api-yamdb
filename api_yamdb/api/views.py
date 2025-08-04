from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (
    ListModelMixin, CreateModelMixin, DestroyModelMixin
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from reviews.models import (
    Category, Genre, Title, Review, Comment)
from .filters import TitleFilter
from .permissions import IsAdminOrReadOnly, IsAuthorOrModeratorOrAdmin
from .serializers import (
    CategorySerializer, GenreSerializer, TitleReadSerializer,
    TitleWriteSerializer, ReviewSerializer, CommentSerializer
)


class BaseCategoryGenreViewSet(
    CreateModelMixin, ListModelMixin, DestroyModelMixin,
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
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter
    permission_classes = [IsAdminOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleReadSerializer
        return TitleWriteSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        ordering = self.queryset.model._meta.ordering
        return queryset.order_by(*ordering)


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
