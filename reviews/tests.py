"""Небольшие тесты на самое важное. Запуск: python manage.py test"""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import DISLIKE, LIKE, Book, Genre, Profile, Reaction, Review


class SiteTests(TestCase):
    def setUp(self):
        # Один пользователь и одна книга нужны почти в каждом тесте.
        self.user = User.objects.create_user(username="vasya", password="Kursovaya2026!")
        self.book = Book.objects.create(
            title="Мастер и Маргарита", author="М. Булгаков", added_by=self.user
        )

    def make_review(self):
        return Review.objects.create(
            book=self.book, author=self.user, title="Отличная книга",
            text="Перечитываю уже третий раз.", rating=5,
        )

    def test_feed_otkryvaetsya(self):
        response = self.client.get(reverse("feed"))
        self.assertEqual(response.status_code, 200)

    def test_zhanry_poyavlyayutsya_sami(self):
        # Миграции 0002 и 0003 добавляют жанры на любой новой базе.
        for name in ("Фантастика", "Детектив", "Ужасы", "Фэнтези"):
            self.assertTrue(Genre.objects.filter(name=name).exists())
        self.assertEqual(Genre.objects.count(), 16)

    def test_registraciya_sozdayot_polzovatelya(self):
        response = self.client.post(reverse("signup"), {
            "username": "petya",
            "password1": "Kursovaya2026!",
            "password2": "Kursovaya2026!",
        })
        self.assertEqual(response.status_code, 302)  # после регистрации — редирект
        self.assertTrue(User.objects.filter(username="petya").exists())
        self.assertEqual(User.objects.get(username="petya").email, "")

    def test_na_vhode_i_registracii_net_pochty(self):
        # Почту мы не спрашиваем ни при входе, ни при регистрации.
        for url in (reverse("login"), reverse("signup")):
            html = self.client.get(url).content.decode()
            self.assertNotIn('name="email"', html)
            self.assertIn('name="username"', html)

    def test_napisat_recenziyu_mozhno_tolko_vojdya(self):
        response = self.client.get(reverse("review_add"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_profil_sozdayotsya_pri_zahode_na_stranicu(self):
        self.client.get(reverse("profile", args=["vasya"]))
        self.assertEqual(Profile.objects.filter(user=self.user).count(), 1)

    def test_laik_ubiraetsya_povtornym_nazhatiem(self):
        review = self.make_review()
        self.client.login(username="vasya", password="Kursovaya2026!")
        like_url = reverse("react", args=[review.pk, "like"])

        self.client.post(like_url)
        self.assertEqual(Reaction.objects.count(), 1)
        self.assertEqual(Reaction.objects.first().value, LIKE)
        self.assertEqual(review.likes_count(), 1)

        self.client.post(like_url)  # нажали ещё раз — лайк снялся
        self.assertEqual(Reaction.objects.count(), 0)

        # Передумали и поменяли лайк на дизлайк: строка в базе одна, не две.
        dislike_url = reverse("react", args=[review.pk, "dislike"])
        self.client.post(like_url)
        self.client.post(dislike_url)
        self.assertEqual(Reaction.objects.count(), 1)
        self.assertEqual(Reaction.objects.first().value, DISLIKE)

    def test_chuzhuyu_recenziyu_ne_otredaktirovat(self):
        review = self.make_review()
        User.objects.create_user(username="petya", password="Kursovaya2026!")
        self.client.login(username="petya", password="Kursovaya2026!")
        response = self.client.get(reverse("review_edit", args=[review.pk]))
        self.assertEqual(response.status_code, 404)
