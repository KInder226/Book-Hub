# Инструкции по установке BookClub Hub

## Шаг 1: Установка зависимостей

1. Создайте виртуальное окружение:
```bash
python -m venv venv
```

2. Активируйте виртуальное окружение:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Шаг 2: Настройка базы данных

1. Установите PostgreSQL (если еще не установлен)

2. Создайте базу данных:
```sql
CREATE DATABASE bookclubhub;
```

3. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

4. Отредактируйте `.env` и укажите настройки базы данных:
```
DB_NAME=bookclubhub
DB_USER=postgres
DB_PASSWORD=ваш_пароль
DB_HOST=localhost
DB_PORT=5432
```

## Шаг 3: Настройка Redis (для Celery и Channels)

Установите и запустите Redis:
- Windows: скачайте с https://github.com/microsoftarchive/redis/releases
- Linux: `sudo apt-get install redis-server`
- Mac: `brew install redis`

Запустите Redis:
```bash
redis-server
```

## Шаг 4: Применение миграций

```bash
python manage.py makemigrations
python manage.py migrate
```

## Шаг 5: Создание суперпользователя

```bash
python manage.py createsuperuser
```

## Шаг 6: Создание начальных данных

Создайте жанры и теги:
```bash
python manage.py shell
```

Затем выполните:
```python
exec(open('manage_commands/create_initial_data.py').read())
```

Или создайте их вручную через админку.

## Шаг 7: Сбор статических файлов

```bash
python manage.py collectstatic
```

## Шаг 8: Запуск сервера

1. Запустите Django сервер разработки:
```bash
python manage.py runserver
```

2. В отдельном терминале запустите Celery worker:
```bash
celery -A bookclubhub worker -l info
```

3. В отдельном терминале запустите Celery beat (для периодических задач):
```bash
celery -A bookclubhub beat -l info
```

4. Убедитесь, что Redis запущен

## Шаг 9: Доступ к сайту

Откройте браузер и перейдите на:
- Основной сайт: http://127.0.0.1:8000/
- Админ-панель: http://127.0.0.1:8000/admin/

## Полезные команды

- Создать фикстуры: `python manage.py dumpdata --indent 2 > fixtures.json`
- Загрузить фикстуры: `python manage.py loaddata fixtures.json`
- Создать миграции: `python manage.py makemigrations`
- Применить миграции: `python manage.py migrate`
- Запустить тесты: `pytest`

## Структура проекта

```
bookclubhub/
├── accounts/          # Приложение пользователей и профилей
├── books/            # Приложение книг и прогресса чтения
├── clubs/            # Приложение книжных клубов
├── discussions/      # Приложение обсуждений (форум)
├── notifications_custom/  # Расширения для уведомлений
├── templates/        # HTML шаблоны
├── static/           # Статические файлы (CSS, JS, изображения)
└── media/            # Загружаемые пользователями файлы
```

## Возможные проблемы

1. **Ошибка подключения к PostgreSQL**: Проверьте настройки в `.env` и убедитесь, что PostgreSQL запущен
2. **Ошибка подключения к Redis**: Убедитесь, что Redis запущен на порту 6379
3. **Ошибки миграций**: Попробуйте удалить все файлы миграций (кроме `__init__.py`) и создать заново
4. **Проблемы со статическими файлами**: Убедитесь, что выполнили `collectstatic`

