from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.tokens import AccessToken

from .constants import USERNAME_PATTERN


User = get_user_model()


class TokenSerializer(serializers.Serializer):
    username = serializers.RegexField(
        required=True,
        regex=USERNAME_PATTERN,
        max_length=150,
    )
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        try:
            user = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            raise NotFound('Пользователь не найден')
        if user.confirmation_code != data['confirmation_code']:
            raise serializers.ValidationError('Неверный код')
        token = AccessToken.for_user(user)
        return {'token': str(token)}


class SignUpSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(regex=USERNAME_PATTERN, max_length=150)
    email = serializers.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('username', 'email',)

    def validate_username(self, username):
        if username.lower() == 'me':
            raise serializers.ValidationError(
                'Недопустимо использование "me" в качестве имени пользователя'
            )
        return username

    def validate(self, data):
        user = User.objects.filter(username=data.get('username')).first()
        email = data.get('email')
        if user:
            if user.email != email:
                raise serializers.ValidationError(
                    'Имя пользователя уже занято другим email.'
                )
        else:
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError(
                    'Email уже используется другим пользователем.'
                )
        return data


class UserSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(regex=USERNAME_PATTERN, max_length=150)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')

    def validate_role(self, role):
        user = self.context['request'].user
        if not (user.is_staff or user.role == 'admin'):
            raise serializers.ValidationError(
                'Вы не можете изменить свою роль.'
            )
        return role
