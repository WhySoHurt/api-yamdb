
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from reviews.constants import RESERVED_WORD, USERNAME_PATTERN


def username_validator(username):
    if username == RESERVED_WORD:
        raise ValidationError('Имя "me" недопустимо')
    validator = RegexValidator(
        regex=USERNAME_PATTERN,
        message='Имя содержит недопустимые символы'
    )
    validator(username)
