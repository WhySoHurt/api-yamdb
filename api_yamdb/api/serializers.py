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
            author = request.user
            title_id = self.context['view'].kwargs.get('title_id')
            if Review.objects.filter(title_id=title_id, author=author).exists():
                raise ValidationError('Вы уже оставляли отзыв к этому произведению.')


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