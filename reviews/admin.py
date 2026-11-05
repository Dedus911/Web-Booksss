"""Чтобы жанры, книги и рецензии было видно в админке /admin/."""

from django.contrib import admin

from .models import Book, Genre, Profile, Reaction, Review

admin.site.register(Genre)
admin.site.register(Book)
admin.site.register(Review)
admin.site.register(Reaction)
admin.site.register(Profile)
