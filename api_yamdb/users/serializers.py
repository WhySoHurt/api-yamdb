from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken


User = get_user_model()


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        try:
            user = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            raise serializers.ValidationError('Пользователь не найден')
        if user.confirmation_code != data['confirmation_code']:
            raise serializers.ValidationError('Неверный код')
        token = AccessToken.for_user(user)
        return {'token': str(token)}


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email',)

    def validate_username(self, username):
        if username.lower() == 'me':
            raise serializers.ValidationError(
                'Недопустимо использование "me" в качестве имени пользователя'
            )
        return username


class UserSerializer(serializers.ModelSerializer):

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
