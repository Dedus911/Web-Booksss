"""Главный список адресов сайта."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Готовые страницы входа и выхода из Django. Мы для них только
    # сделали шаблон templates/registration/login.html.
    path("accounts/", include("django.contrib.auth.urls")),
    # Все остальные страницы — в нашем приложении.
    path("", include("reviews.urls")),
]
