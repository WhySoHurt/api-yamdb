from django.contrib.auth import get_user_model
from django.db import models

from .constants import CHOICES_SCORE, SLUG_MAX_LENGTH, CHAR_MAX_LENGTH


User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=CHAR_MAX_LENGTH)
    slug = models.SlugField(unique=True, max_length=SLUG_MAX_LENGTH)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Genre(models.Model):
    name = models.CharField(max_length=CHAR_MAX_LENGTH)
    slug = models.SlugField(unique=True, max_length=SLUG_MAX_LENGTH)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(max_length=CHAR_MAX_LENGTH)
    year = models.IntegerField()
    description = models.TextField(blank=True)
    genre = models.ManyToManyField(Genre, related_name='titles')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name='titles')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'


class Review(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    score = models.IntegerField(choices=CHOICES_SCORE)
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'], name='unique_review')
        ]

    def __str__(self):
        return f"{self.author.username} - {self.title.name}"


class Comment(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f"{self.author.username} - {self.review}"
