"""Файл для запуска на настоящем сервере. В курсовой мы его не трогаем."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "book_platform.settings")
application = get_wsgi_application()
