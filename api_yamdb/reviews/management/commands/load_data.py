import csv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from reviews.models import Category, Genre, Title


User = get_user_model()


class Command(BaseCommand):
    """
    Кастомная команда Django для загрузки данных из CSV-файлов в базу данных.

    Пример использования:
        python manage.py load_data --path static/data

    Ожидается, что в указанной папке находятся следующие файлы:
        - category.csv
        - genre.csv
        - titles.csv
        - genre_title.csv (связь ManyToMany между Title и Genre)
    """

    help = 'Загружает данные из CSV-файлов в базу данных'

    def add_arguments(self, parser):
        """
        Определяем аргументы командной строки.

        Добавляем опцию --path, чтобы пользователь мог указать путь
        к папке с CSV-файлами.
        """

        parser.add_argument(
            '--path', type=str, help='Путь к папке с CSV-файлами')

    def handle(self, *args, **options):
        """
        Основной метод, который выполняется при запуске команды.

        Здесь мы:
        1. Получаем путь к файлам.
        2. Проверяем, указан ли путь.
        3. Последовательно загружаем данные в каждую модель.
        """

        path = options['path']

        # Если путь не указан — выводим ошибку и завершаем выполнение.
        if not path:
            self.stdout.write(
                self.style.ERROR(
                    'Укажите путь к папке с CSV-файлами: --path /путь/к/папке'
                )
            )
            return

        # Вызываем методы для загрузки данных по каждому файлу
        self.load_categories(f'{path}/category.csv')
        self.load_genres(f'{path}/genre.csv')
        self.load_titles(f'{path}/titles.csv')
        self.load_genre_title(f'{path}/genre_title.csv')

        # Сообщаем об успешном завершении
        self.stdout.write(
            self.style.SUCCESS('Все данные успешно загружены в базу данных!')
        )

    def load_categories(self, file_path):
        """
        Загружает категории из CSV-файла.

        Формат файла (category.csv):
            id,name,slug
        """

        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Используем get_or_create(), чтобы избежать дубликатов.
                Category.objects.get_or_create(
                    id=row['id'],
                    defaults={  # Если объекта нет — создаём с этими полями
                        'name': row['name'],
                        'slug': row['slug']
                    }
                )
        self.stdout.write(self.style.SUCCESS('Категории загружены'))

    def load_genres(self, file_path):
        """
        Загружает жанры из CSV-файла.

        Формат файла (genre.csv):
            id,name,slug
        """
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Genre.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'name': row['name'],
                        'slug': row['slug']
                    }
                )
        self.stdout.write(self.style.SUCCESS('Жанры загружены'))

    def load_titles(self, file_path):
        """
        Загружает произведения из CSV-файла.

        Формат файла (titles.csv):
            id,name,year,category

        Поле category — внешний ключ, поэтому ищем объект Category по id.
        """

        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                category = (Category.objects.get(id=row['category'])
                            if row['category'] else None)
                Title.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'name': row['name'],
                        'year': int(row['year']),
                        'description': row.get('description', ''),
                        'category': category
                    }
                )
        self.stdout.write(self.style.SUCCESS('Произведения загружены'))

    def load_genre_title(self, file_path):
        """
        Привязывает жанры к произведениям через ManyToMany-связь.

        Формат файла (genre_title.csv):
            id,title_id,genre_id
        """

        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                title = Title.objects.get(id=row['title_id'])
                genre = Genre.objects.get(id=row['genre_id'])
                title.genre.add(genre)
        self.stdout.write(
            self.style.SUCCESS('Жанры к произведениям привязаны'))
