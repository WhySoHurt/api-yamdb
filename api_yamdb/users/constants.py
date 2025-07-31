USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
ROLE_CHOICES = [
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор')
]
USERNAME_PATTERN = r'^[\w.@+-]+\Z'
