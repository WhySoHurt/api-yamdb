from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from reviews.constants import (
    CONFIRMATION_CODE_LENGTH,
    EMAIL_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
    USERNAME_PATTERN,
)
from reviews.models import Category, Comment, Genre, Review, Title
from reviews.validators import username_validator

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели отзывов.

    Автор подставляется автоматически в ReviewViewSet.
    """

    author = serializers.SlugRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
        slug_field='username',
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        """
        Проверяет, что пользователь ещё не оставлял отзыв к произведению.
        """
        request = self.context['request']
        if request.method != 'POST':
            return data

        title_id = self.context['view'].kwargs['title_pk']

        if Review.objects.filter(
            title_id=title_id, author=request.user
        ).exists():
            title_name = Title.objects.get(pk=title_id).name
            raise ValidationError(
                f'Отзыв пользователя {request.user.username}'
                f'к произведению {title_name} уже существует.'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели комментариев.

    Автор подставляется автоматически в ReviewViewSet.
    """

    author = serializers.SlugRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
        slug_field='username',
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    """Для вывода информации о произведении."""

    rating = serializers.IntegerField(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )
        read_only_fields = fields


class TitleWriteSerializer(serializers.ModelSerializer):
    """Для создания/обновления произведения."""

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        required=False,
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all(), required=False
    )

    class Meta:
        model = Title
        fields = ('name', 'year', 'description', 'genre', 'category')

    def to_representation(self, instance):
        """
        Используем TitleReadSerializer для сериализации данных при выводе.
        """
        return TitleReadSerializer(instance, context=self.context).data


class TokenSerializer(serializers.Serializer):
    username = serializers.RegexField(
        required=True,
        regex=USERNAME_PATTERN,
        max_length=USERNAME_MAX_LENGTH,
        validators=[username_validator],
    )
    confirmation_code = serializers.CharField(
        required=True, max_length=CONFIRMATION_CODE_LENGTH
    )


class SignUpSerializer(serializers.Serializer):
    username = serializers.RegexField(
        required=True,
        regex=USERNAME_PATTERN,
        max_length=USERNAME_MAX_LENGTH,
        validators=[username_validator],
    )
    email = serializers.EmailField(required=True, max_length=EMAIL_MAX_LENGTH)


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        validators=[
            username_validator,
            UniqueValidator(
                queryset=User.objects.all(),
                message='Пользователь с таким username уже существует.',
            ),
        ],
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
