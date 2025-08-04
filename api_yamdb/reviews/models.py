import datetime

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .constants import (
    ADMIN,
    CHOICES_SCORE,
    EMAIL_MAX_LENGTH,
    MODERATOR,
    NAME_MAX_LENGTH,
    ROLE_CHOICES,
    ROLE_MAX_LENGTH,
    SLUG_MAX_LENGTH,
    USER,
    USERNAME_MAX_LENGTH,
    USERNAME_PATTERN,
)


class YamdbUser(AbstractUser):
    username = models.CharField(
        unique=True,
        max_length=USERNAME_MAX_LENGTH,
        verbose_name='Имя пользователя',
        validators=[RegexValidator(regex=USERNAME_PATTERN)]
    )
    email = models.EmailField(unique=True, max_length=EMAIL_MAX_LENGTH)
    first_name = models.CharField('Имя', max_length=150, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Права доступа',
        max_length=ROLE_MAX_LENGTH,
        choices=ROLE_CHOICES,
        default=USER,
    )
    confirmation_code = models.CharField(max_length=128, blank=True)

    REQUIRED_FIELDS = ('email',)

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser or self.is_staff

    @property
    def is_moderator(self):
        return self.role == MODERATOR


def current_year():
    return datetime.date.today().year


class NamedSlugModel(models.Model):
    """
    Абстрактный базовый класс для моделей с полями name и slug.
    Предназначен для наследования моделями Category и Genre.
    """

    name = models.CharField(
        max_length=NAME_MAX_LENGTH, verbose_name='Название')
    slug = models.SlugField(
        unique=True, max_length=SLUG_MAX_LENGTH, verbose_name='Слаг')

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(NamedSlugModel):

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Genre(NamedSlugModel):

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(
        max_length=NAME_MAX_LENGTH, verbose_name='Название')
    year = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(current_year)
        ],
        verbose_name='Год'
    )
    description = models.TextField(blank=True, verbose_name='Описание')
    genre = models.ManyToManyField(
        Genre, related_name='titles', verbose_name='Жанр')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True,
        related_name='titles', verbose_name='Категория'
    )

    class Meta:
        ordering = ('-year', 'name')
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class ReviewCommentBase(models.Model):
    """
    Абстрактный базовый класс для отзывов и комментариев.
    """

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор')
    text = models.TextField(verbose_name='Текст отзыва')
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации')

    class Meta:
        abstract = True
        ordering = ('-pub_date',)


class Review(ReviewCommentBase):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, verbose_name='Произведение')
    score = models.IntegerField(
        choices=CHOICES_SCORE, verbose_name='Оценка')

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = 'reviews'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'], name='unique_review'
            )
        ]

    def __str__(self):
        return f'{self.author.username} - {self.title.name}'


class Comment(ReviewCommentBase):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, verbose_name='Отзыв')

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'

    def __str__(self):
        return f'{self.author.username} - {self.review}'
