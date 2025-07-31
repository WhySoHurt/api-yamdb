from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from rest_framework import permissions, status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .pagination import UserPagination
from .permissions import IsAdmin
from .serializers import SignUpSerializer, TokenSerializer, UserSerializer

User = get_user_model()


class TokenView(APIView):
    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class SignUpView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        user = User.objects.filter(username=username, email=email).first()
        if user:
            if user.email != email:
                return Response(
                    {'email':
                     'Email не соответствует существующему пользователю'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.confirmation_code = get_random_string(length=20)
            user.save()
        else:
            user = User.objects.create(
                username=username,
                email=email,
                confirmation_code=get_random_string(length=20)
            )
        send_mail(
            'Код подтверждения',
            f'Ваш код: {user.confirmation_code}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=True
        )
        return Response(
            {'email': email, 'username': username},
            status=status.HTTP_200_OK
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    pagination_class = UserPagination
    lookup_field = 'username'

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='me'
    )
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        if request.method == 'PATCH':
            if 'role' in request.data:
                return Response(
                    {'role': 'Данное поле недоступно для редактирования'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.get_serializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """Переопределение для PATCH, блокировка PUT"""
        if request.method == 'PUT':
            return Response(
                {'detail': 'Метод PUT не поддерживается'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')
        if not username or not email:
            return Response(
                {'detail': 'Необходимо указать username и email'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = User.objects.filter(username=username).first()
        if user:
            if user.email != email:
                return Response(
                    {'username': 'Имя пользователя уже занято другим email.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if User.objects.filter(email=email).exists():
            return Response(
                {'email': 'Email уже используется другим пользователем.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().create(request, *args, **kwargs)
