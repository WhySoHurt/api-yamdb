import string


MIN_SCORE = 1
MAX_SCORE = 10
SLUG_MAX_LENGTH = 50
NAME_MAX_LENGTH = 256
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
