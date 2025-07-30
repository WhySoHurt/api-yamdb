from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import ROLE_CHOICES, USER, ADMIN, MODERATOR


class MyUser(AbstractUser):
    username = models.CharField(
        unique=True,
        max_length=150
    )
    email = models.EmailField(unique=True, max_length=254)
    first_name = models.CharField('Имя', max_length=150, blank=True)
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=True
    )
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Права доступа',
        max_length=20,
        choices=ROLE_CHOICES,
        default=USER
    )
    confirmation_code = models.CharField(max_length=128, blank=True)

    REQUIRED_FIELDS = ('email',)

    class Meta:
        ordering = ('id',)
        verbose_name = 'User'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == MODERATOR
