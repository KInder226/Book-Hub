# Команды управления

## Создание начальных данных

Для создания жанров и тегов постов:

```bash
python manage.py shell
```

Затем в консоли:
```python
exec(open('manage_commands/create_initial_data.py').read())
```

Или используйте фикстуры:
```bash
python manage.py loaddata initial_data.json
```

