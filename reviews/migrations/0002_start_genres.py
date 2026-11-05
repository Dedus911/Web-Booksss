"""Миграция не про таблицы, а про данные: добавляем стартовые жанры.

Обычная миграция создаёт таблицы, а эта просто кладёт несколько строк
в уже готовую таблицу Genre. Благодаря ей на новом компьютере после
`python manage.py migrate` список жанров сразу заполнен.
"""

from django.db import migrations

START_GENRES = [
    "Фантастика",
    "Классика",
    "Детектив",
    "Нон-фикшн",
    "Приключения",
    "Поэзия",
]


def add_genres(apps, schema_editor):
    Genre = apps.get_model("reviews", "Genre")
    for name in START_GENRES:
        # get_or_create: если жанр уже есть, второй раз его не создаём.
        Genre.objects.get_or_create(name=name)


def remove_genres(apps, schema_editor):
    # Эта функция нужна, чтобы миграцию можно было откатить.
    Genre = apps.get_model("reviews", "Genre")
    Genre.objects.filter(name__in=START_GENRES).delete()


class Migration(migrations.Migration):
    dependencies = [("reviews", "0001_initial")]

    operations = [migrations.RunPython(add_genres, remove_genres)]
