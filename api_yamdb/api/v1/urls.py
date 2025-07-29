from django.urls import path, include
from users.views import SignUpView, TokenView
from rest_framework.routers import DefaultRouter


v1_router = DefaultRouter()

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/signup/', SignUpView.as_view(), name='signup'),
    path('auth/token/', TokenView.as_view(), name='token'),
]
