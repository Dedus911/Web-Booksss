"""Ещё одна миграция с данными: добавляем жанры, которых не было в 0002.

Первая миграция с жанрами уже выполнена на всех базах, поэтому новые
жанры дописываем отдельной миграцией. Так они появятся и у тех, кто
уже запускал проект раньше.
"""

from django.db import migrations

MORE_GENRES = [
    "Ужасы",
    "Фэнтези",
    "Триллер",
    "Мистика",
    "Роман",
    "Историческая проза",
    "Биография",
    "Детская литература",
    "Психология",
    "Юмор",
]


def add_more_genres(apps, schema_editor):
    Genre = apps.get_model("reviews", "Genre")
    for name in MORE_GENRES:
        Genre.objects.get_or_create(name=name)


def remove_more_genres(apps, schema_editor):
    # Нужно, чтобы миграцию можно было откатить.
    Genre = apps.get_model("reviews", "Genre")
    Genre.objects.filter(name__in=MORE_GENRES).delete()


class Migration(migrations.Migration):
    dependencies = [("reviews", "0002_start_genres")]

    operations = [migrations.RunPython(add_more_genres, remove_more_genres)]
