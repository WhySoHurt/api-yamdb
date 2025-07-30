import datetime

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from reviews.models import Category, Genre, Title, Review, Comment


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели отзывов.

    Автор подставляется автоматически в ReviewViewSet.
    """
    
    author = serializers.StringRelatedField(
        read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('author',)
        model = Review

    def validate(self, data):
        """
        Проверяет, что пользователь ещё не оставлял отзыв к произведению.
        """
        request = self.context['request']
        if request.method == 'POST':
            title_id = self.context['view'].kwargs.get('title_pk')
            if Review.objects.filter(title_id=title_id, author=request.user).exists():
                raise ValidationError('Вы уже оставляли отзыв к этому произведению.')
            
        return data


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели комментариев.

    Автор подставляется автоматически в ReviewViewSet.
    """

    author = serializers.StringRelatedField(
        read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('author',)
        model = Comment


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Для вывода информации о произведении."""

    rating = serializers.IntegerField(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category')
        read_only_fields = ('id',)


class TitleCreateSerializer(serializers.ModelSerializer):
    """Для создания/обновления произведения."""

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def validate_year(self, proposed_year):
        current_year = datetime.date.today().year
        if proposed_year > current_year:
            raise ValidationError(
                f'Год выпуска не может быть больше текущего ({current_year}). '
                'Нельзя добавлять произведения из будущего.'
            )
        return proposed_year
