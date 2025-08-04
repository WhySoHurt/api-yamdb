import string

CHOICES_SCORE = [(i, str(i)) for i in range(1, 11)]
SLUG_MAX_LENGTH = 50
CHAR_MAX_LENGTH = 256
USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
ROLE_CHOICES = [
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор')
]
USERNAME_PATTERN = r'^[\w.@+-]+\Z'
USERNAME_MAX_LENGTH = 150
EMAIL_MAX_LENGTH = 254
ROLE_MAX_LENGTH = 20
CONFIRMATION_CODE_LENGTH = 20
CONFIRMATION_CODE_CHARS = string.ascii_uppercase + string.digits
INVALID_USERNAME = 'me'
EDIT_ENDPOINT = 'me'
