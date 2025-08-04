# api_yamdb

Проект **API для платформы с отзывами на произведения** позволяет пользователям оставлять отзывы и комментарии к фильмам, книгам, музыке и другим произведениям. Проект реализован на Django REST Framework и соответствует REST-архитектуре.

## Авторы

- Иван Ильницкий
    [GitHub](https://github.com/WhySoHurt) | deddotu@yandex.ru
- Илья Горбачев
    [GitHub](https://github.com/IlyaGorbachev01) | ilya-gorbachev01@yandex.ru
- Назар Турани
    [GitHub](https://github.com/NazarioTurani) | turani.nazar2012@yandex.ru

## Техно-стек

- **Python** 3.9+
- **Django** 4.2+
- **Django REST Framework** (DRF)
- **Django Filters** - фильтрация по полям
- **SQLite**
- **python-dotenv** - управление переменными окружения
- **Simple JWT** - аутентификация через JWT

## Команды для развёртывания

### 1. Клонирование репозитория

```bash
git clone https://github.com/WhySoHurt/api-yamdb.git
cd api-yamdb
```

### 2. Создание виртуального окружения

```python
python -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows
```

### 3. Установка зависимостей

```python
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

Создайте файл .env в корне проекта:

```
SECRET_KEY=ваш_секретный_ключ
DEBUG=False
```

### 5. Применение миграций

```python
python manage.py migrate
```

### 6. Импорт данных из CSV-фикстур

```python
python manage.py load_data --path static/data
```

Ожидается, что в указанной папке находятся следующие файлы:
- category.csv
- genre.csv
- titles.csv
- genre_title.csv (связь ManyToMany между Title и Genre)
- users.csv
- comments.csv
- review.csv

### 7. Запуск сервера

```python
python manage.py runserver
```

## Доступ к справке по API 

После запуска сервера: 
Redoc (документация API) — http://localhost:8000/redoc/
Подробная документация с примерами запросов, описанием эндпоинтов и кодов ответов.
