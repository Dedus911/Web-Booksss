#!/usr/bin/env python
"""Обычный manage.py: через него запускают сервер, миграции и тесты."""

import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "book_platform.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Похоже, Django не установлен. Сначала выполни: pip install -r requirements.txt"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
