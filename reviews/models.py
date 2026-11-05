"""Модели: один класс — одна таблица в базе данных."""

from django.contrib.auth.models import User
from django.db import models

# Договорились: лайк хранится как 1, дизлайк как -1.
# Число удобнее, чем две разные таблицы или два булевых поля.
LIKE = 1
DISLIKE = -1
REACTION_CHOICES = ((LIKE, "Лайк"), (DISLIKE, "Дизлайк"))

# Оценка книги от 1 до 5. В шаблоне её превратим в звёздочки.
RATING_CHOICES = (
    (1, "1 — не понравилась"),
    (2, "2 — слабо"),
    (3, "3 — нормально"),
    (4, "4 — хорошо"),
    (5, "5 — отлично"),
)


class Genre(models.Model):
    name = models.CharField("Название жанра", max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField("Название", max_length=200)
    author = models.CharField("Автор книги", max_length=200)
    year = models.PositiveSmallIntegerField("Год издания", blank=True, null=True)
    genre = models.ForeignKey(
        Genre, verbose_name="Жанр", blank=True, null=True,
        on_delete=models.SET_NULL, related_name="books",
    )
    description = models.TextField("Краткое описание", blank=True)
    # Кто добавил книгу на сайт. Пригодится, чтобы видно было, откуда книга.
    added_by = models.ForeignKey(
        User, verbose_name="Добавил", on_delete=models.CASCADE, related_name="books"
    )
    created_at = models.DateTimeField("Дата добавления", auto_now_add=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Книга"
        verbose_name_plural = "Книги"

    def __str__(self):
        return f"{self.title} — {self.author}"


class Review(models.Model):
    book = models.ForeignKey(
        Book, verbose_name="Книга", on_delete=models.CASCADE, related_name="reviews"
    )
    author = models.ForeignKey(
        User, verbose_name="Автор рецензии", on_delete=models.CASCADE, related_name="reviews"
    )
    title = models.CharField("Заголовок", max_length=200)
    text = models.TextField("Текст рецензии")
    rating = models.IntegerField("Оценка", choices=RATING_CHOICES, default=5)
    created_at = models.DateTimeField("Дата публикации", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]  # сначала свежие
        verbose_name = "Рецензия"
        verbose_name_plural = "Рецензии"

    def __str__(self):
        return self.title

    def likes_count(self):
        # related_name="reactions" — это все реакции на эту рецензию.
        return self.reactions.filter(value=LIKE).count()

    def dislikes_count(self):
        return self.reactions.filter(value=DISLIKE).count()

    def stars(self):
        # Django сам вызывает методы без аргументов прямо из шаблона.
        return "★" * self.rating + "☆" * (5 - self.rating)


class Reaction(models.Model):
    review = models.ForeignKey(
        Review, verbose_name="Рецензия", on_delete=models.CASCADE, related_name="reactions"
    )
    user = models.ForeignKey(
        User, verbose_name="Пользователь", on_delete=models.CASCADE, related_name="reactions"
    )
    value = models.SmallIntegerField("Оценка", choices=REACTION_CHOICES)

    class Meta:
        # Один человек — одна реакция на одну рецензию.
        # База сама не даст положить две строки с той же парой.
        unique_together = (("review", "user"),)
        verbose_name = "Реакция"
        verbose_name_plural = "Реакции"

    def __str__(self):
        return f"{self.user.username}: {self.get_value_display()}"


class Profile(models.Model):
    user = models.OneToOneField(
        User, verbose_name="Пользователь", on_delete=models.CASCADE, related_name="profile"
    )
    bio = models.TextField("О себе", blank=True)
    favorite_genre = models.ForeignKey(
        Genre, verbose_name="Любимый жанр", blank=True, null=True,
        on_delete=models.SET_NULL, related_name="fans",
    )
    created_at = models.DateTimeField("Дата регистрации на сайте", auto_now_add=True)

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"Профиль: {self.user.username}"


def get_profile(user):
    """Отдаём профиль, а если его ещё нет — сразу создаём.

    Так не надо разбираться с сигналами Django: профиль появится,
    когда человек первый раз зайдёт на свою страницу.
    """
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile
