"""То же, что wsgi.py, но для асинхронного запуска. Нам он пока не нужен."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "book_platform.settings")
application = get_asgi_application()
