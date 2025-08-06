import datetime

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator
)
from django.db import models

from .constants import (
    ADMIN,
    CONFIRMATION_CODE_LENGTH,
    EMAIL_MAX_LENGTH,
    MAX_SCORE,
    MIN_SCORE,
    MODERATOR,
    NAME_MAX_LENGTH,
    SLUG_MAX_LENGTH,
    USER,
    USERNAME_MAX_LENGTH,
    USERNAME_PATTERN,
)
from .validators import username_validator

ROLE_CHOICES = [
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
]


class YamdbUser(AbstractUser):
    username = models.CharField(
        unique=True,
        max_length=USERNAME_MAX_LENGTH,
        verbose_name='Пользователь',
        validators=[
            RegexValidator(regex=USERNAME_PATTERN),
            username_validator,
        ],
    )
    email = models.EmailField(unique=True, max_length=EMAIL_MAX_LENGTH)
    first_name = models.CharField('Имя', max_length=150, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)
    bio = models.TextField('Описание профиля', blank=True)
    role = models.CharField(
        'Роль',
        max_length=max(len(role[0]) for role in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER,
    )
    confirmation_code = models.CharField(
        max_length=CONFIRMATION_CODE_LENGTH, blank=True
    )

    REQUIRED_FIELDS = ('email',)

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_staff

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
        max_length=NAME_MAX_LENGTH, verbose_name='Название'
    )
    slug = models.SlugField(
        unique=True, max_length=SLUG_MAX_LENGTH, verbose_name='Слаг'
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(NamedSlugModel):
    class Meta(NamedSlugModel.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Genre(NamedSlugModel):
    class Meta(NamedSlugModel.Meta):
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(
        max_length=NAME_MAX_LENGTH, verbose_name='Название'
    )
    year = models.IntegerField(
        validators=[MaxValueValidator(current_year)],
        verbose_name='Год',
    )
    description = models.TextField(blank=True, verbose_name='Описание')
    genre = models.ManyToManyField(Genre, verbose_name='Жанр')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )

    class Meta:
        ordering = ('-year', 'name')
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'
        default_related_name = 'titles'

    def __str__(self):
        return self.name


class ReviewCommentBase(models.Model):
    """
    Абстрактный базовый класс для отзывов и комментариев.
    """

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации'
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)
        default_related_name = '%(class)ss'


class Review(ReviewCommentBase):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, verbose_name='Произведение'
    )
    score = models.IntegerField(
        validators=[
            MinValueValidator(MIN_SCORE),
            MaxValueValidator(MAX_SCORE)
        ],
        verbose_name='Оценка')

    class Meta(ReviewCommentBase.Meta):
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'], name='unique_review'
            )
        ]

    def __str__(self):
        return f'{self.author.username} - {self.title.name}'


class Comment(ReviewCommentBase):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, verbose_name='Отзыв'
    )

    class Meta(ReviewCommentBase.Meta):
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.author.username} - {self.review}'
