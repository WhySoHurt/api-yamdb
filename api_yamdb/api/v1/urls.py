from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import SignUpView, TokenView
from api.views import CategoryViewSet, GenreViewSet, TitleViewSet
from users.views import UserViewSet


v1_router = DefaultRouter()
v1_router.register('users', UserViewSet, basename='users')
v1_router.register('categories', CategoryViewSet)
v1_router.register('genres', GenreViewSet)
v1_router.register('titles', TitleViewSet)


urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/signup/', SignUpView.as_view(), name='signup'),
    path('auth/token/', TokenView.as_view(), name='token'),
]
