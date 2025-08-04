import re

from django.core.exceptions import ValidationError

from reviews.constants import USERNAME_PATTERN


def username_validator(username):
    if username == 'me':
        raise ValidationError('Имя "me" недопустимо')
    if not re.match(USERNAME_PATTERN, username):
        raise ValidationError('Имя содержит недопустимые символы')
