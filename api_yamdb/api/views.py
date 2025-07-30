from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.filters import SearchFilter

from reviews.models import (
    Category, Genre, Title, Review, Comment)
from .filters import TitleFilter
from .permissions import IsAdminOrReadOnly
from .serializers import (
    CategorySerializer, GenreSerializer, TitleSerializer, TitleCreateSerializer,
    ReviewSerializer, CommentSerializer
)
from .pagination import ReviewCommentPagination
from .mixins import ReviewCommentPermissionMixin


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['name']
    search_fields = ['name']
    permission_classes = [IsAdminOrReadOnly]


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['name']
    search_fields = ['name']
    permission_classes = [IsAdminOrReadOnly]


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score')).all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleSerializer
        return TitleCreateSerializer


class ReviewViewSet(ReviewCommentPermissionMixin, viewsets.ModelViewSet):
    """Вьюсет для запросов к отзывам."""

    serializer_class = ReviewSerializer
    pagination_class = ReviewCommentPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        """Получает произведение по id из kwarg-аргумента."""
        return Review.objects.filter(title_id=self.kwargs['title_pk'])
    
    def perform_create(self, serializer):
        """Сохраняет автора и проверяет, что произведение существует."""
        title = get_object_or_404(Title, pk=self.kwargs['title_pk'])
        serializer.save(author=self.request.user, title=title)



class CommentViewSet(ReviewCommentPermissionMixin, viewsets.ModelViewSet):
    """Вьюсет для запросов к комментариям."""

    serializer_class = CommentSerializer
    pagination_class = ReviewCommentPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        """Получает комментарий по id произведения из kwarg-аргумента."""

        return Comment.objects.filter(review_id=self.kwargs['review_pk'])

    def perform_create(self, serializer):
        """Сохраняет автора и проверяет, что отзыв существует."""
        
        review = get_object_or_404(Review, pk=self.kwargs['review_pk'])
        serializer.save(author=self.request.user, review=review)
