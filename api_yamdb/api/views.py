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

    def get_title(self):
        """Возвращает произведение по pk, указанному в URL."""
        return get_object_or_404(Title, pk=self.kwargs['title_pk'])

    def get_queryset(self):
        """Возвращает отзыв к произведению."""
        return Review.objects.filter(title=self.get_title())
    
    def perform_create(self, serializer):
        """Сохраняет отзыв, подставляя автора и произведение."""
        serializer.save(author=self.request.user, title=self.get_title())



class CommentViewSet(ReviewCommentPermissionMixin, viewsets.ModelViewSet):
    """Вьюсет для запросов к комментариям."""

    serializer_class = CommentSerializer
    pagination_class = ReviewCommentPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_review(self):
        """Возвращает отзыв по pk, указанному в URL."""
        return get_object_or_404(Review, pk=self.kwargs['review_pk'])

    def get_queryset(self):
        """Возвращает комментарий к отзыву."""
        return Comment.objects.filter(review=self.get_review())

    def perform_create(self, serializer):
        """Сохраняет комментарий, подставляя автора и отзыв."""
        serializer.save(author=self.request.user, review=self.get_review())
