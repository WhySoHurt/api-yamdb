from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from reviews.constants import EDIT_PROFILE_URL, USERNAME_PATTERN

USERNAME_REGEX_VALIDATOR = RegexValidator(
    regex=USERNAME_PATTERN, message='Имя содержит недопустимые символы'
)


def username_validator(username):
    if username == EDIT_PROFILE_URL:
        raise ValidationError(f'Имя {EDIT_PROFILE_URL} недопустимо')
    USERNAME_REGEX_VALIDATOR(username)
    return username
