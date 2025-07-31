from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from users.views import SignUpView, TokenView
from api.views import (
    CategoryViewSet, GenreViewSet, TitleViewSet,
    ReviewViewSet, CommentViewSet)
from users.views import UserViewSet


v1_router = DefaultRouter()
v1_router.register('users', UserViewSet, basename='users')
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('titles', TitleViewSet, basename='titles')

review_router = routers.NestedSimpleRouter(
    v1_router,
    r'titles',
    lookup='title'
)
review_router.register(r'reviews', ReviewViewSet, basename='title-reviews')

comment_router = routers.NestedSimpleRouter(
    review_router,
    r'reviews',
    lookup='review'
)
comment_router.register(
    r'comments',
    CommentViewSet,
    basename='reviews-comment'
)

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/signup/', SignUpView.as_view(), name='signup'),
    path('auth/token/', TokenView.as_view(), name='token'),
    path('', include(review_router.urls)),
    path('', include(comment_router.urls)),
]
