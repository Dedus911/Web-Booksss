"""Формы: что видит человек на странице и что мы проверяем перед сохранением."""

from datetime import date

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Book, Profile, Review


class SignUpForm(UserCreationForm):
    # Берём готовую форму Django и явно перечисляем поля:
    # логин, пароль и подтверждение пароля. Почту не спрашиваем.
    class Meta:
        model = User
        fields = ("username", "password1", "password2")


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ("title", "author", "year", "genre", "description")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_year(self):
        # Небольшая своя проверка: книга из будущего нам не нужна.
        year = self.cleaned_data.get("year")
        if year and year > date.today().year:
            raise forms.ValidationError("Год издания не может быть в будущем.")
        return year


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("book", "title", "rating", "text")
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Например: не смог оторваться"}),
            "text": forms.Textarea(attrs={"rows": 9}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("bio", "favorite_genre")
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4, "placeholder": "Пара слов о себе и о книгах"}),
        }
