"""Адреса страниц нашего приложения."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.feed, name="feed"),
    path("signup/", views.signup, name="signup"),
    path("review/new/", views.review_add, name="review_add"),
    path("review/<int:pk>/", views.review_detail, name="review_detail"),
    path("review/<int:pk>/edit/", views.review_edit, name="review_edit"),
    path("review/<int:pk>/delete/", views.review_delete, name="review_delete"),
    path("review/<int:pk>/react/<str:action>/", views.react, name="react"),
    path("book/new/", views.book_add, name="book_add"),
    path("book/<int:pk>/", views.book_detail, name="book_detail"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("user/<str:username>/", views.profile, name="profile"),
]
