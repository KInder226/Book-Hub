"""
Скрипт для создания начальных данных (жанры, теги постов)
Запуск: python manage.py shell < manage_commands/create_initial_data.py
"""

from books.models import Genre
from discussions.models import PostTag

# Создание жанров
genres_data = [
    'Фантастика',
    'Фэнтези',
    'Детектив',
    'Роман',
    'Драма',
    'Приключения',
    'Историческая проза',
    'Научная литература',
    'Биография',
    'Поэзия',
    'Комедия',
    'Триллер',
    'Хоррор',
    'Мистика',
    'Юмор',
]

for genre_name in genres_data:
    Genre.objects.get_or_create(name=genre_name, defaults={'slug': genre_name.lower().replace(' ', '-')})
    print(f'Создан жанр: {genre_name}')

# Создание тегов постов
tags_data = [
    {'name': 'Вопрос', 'slug': 'vopros', 'color': '#007bff'},
    {'name': 'Спойлер', 'slug': 'spoyler', 'color': '#dc3545'},
    {'name': 'Цитата', 'slug': 'tsitata', 'color': '#28a745'},
    {'name': 'Обсуждение', 'slug': 'obsuzhdenie', 'color': '#17a2b8'},
    {'name': 'Рекомендация', 'slug': 'rekomendatsiya', 'color': '#ffc107'},
]

for tag_data in tags_data:
    PostTag.objects.get_or_create(
        slug=tag_data['slug'],
        defaults={
            'name': tag_data['name'],
            'color': tag_data['color']
        }
    )
    print(f'Создан тег: {tag_data["name"]}')

print('\nНачальные данные успешно созданы!')

