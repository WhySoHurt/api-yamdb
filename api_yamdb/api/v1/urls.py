from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import SignUpView, TokenView


v1_router = DefaultRouter()

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/signup/', SignUpView.as_view(), name='signup'),
    path('auth/token/', TokenView.as_view(), name='token'),
]
