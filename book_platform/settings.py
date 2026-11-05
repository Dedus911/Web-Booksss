"""Настройки проекта. Почти всё здесь — стандарт из django-admin startproject."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Ключ нужен Django для кук и защиты форм. Для курсовой оставляю прямо тут,
# но на настоящем сайте его надо хранить в переменных окружения.
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY", "uchebnyi-proekt-pro-retsenzii-na-knigi-2026-ne-dlya-boevogo-saita"
)

DEBUG = True

# "*" удобно на защите: сайт откроется и по localhost, и по внешней ссылке.
ALLOWED_HOSTS = ["*"]

# Если сайт открыт через прокси по внешней ссылке, прокси сообщает про https.
# Иначе Django решит, что форма пришла с другого адреса, и не пустит её.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = ["https://*.e2b.app"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "reviews",  # наше приложение
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "book_platform.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "book_platform.wsgi.application"

# SQLite — файл рядом с проектом. Для курсовой этого более чем хватает:
# не надо поднимать отдельный сервер базы данных.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Куда отправлять человека, который не вошёл в аккаунт, и куда после входа.
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "feed"
LOGOUT_REDIRECT_URL = "feed"
