"""Вьюхи: получаем запрос, работаем с базой, отдаём страницу.

Все вьюхи здесь — обычные функции. Специально не стал использовать
классы и прочие сложные штуки: так код легче читать и объяснять.
"""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import BookForm, ProfileForm, ReviewForm, SignUpForm
from .models import DISLIKE, LIKE, Book, Genre, Reaction, Review, get_profile


def mark_my_reactions(reviews, user):
    """Дописываем к каждой рецензии реакцию текущего пользователя.

    В шаблоне нельзя вызвать функцию с аргументом, поэтому заранее
    приклеиваем к каждой рецензии две готовые галочки: i_liked и i_disliked.
    По ним в шаблоне подсвечиваем нажатую кнопку.
    """
    reviews = list(reviews)
    ids = [review.pk for review in reviews]
    my = {}
    if user.is_authenticated and ids:
        pairs = Reaction.objects.filter(user=user, review_id__in=ids).values_list(
            "review_id", "value"
        )
        my = dict(pairs)  # получится словарь вида {номер рецензии: 1 или -1}
    for review in reviews:
        value = my.get(review.pk, 0)  # 0 — человек ещё не оценивал
        review.i_liked = value == LIKE
        review.i_disliked = value == DISLIKE
    return reviews


def feed(request):
    """Главная страница: лента рецензий с поиском и фильтрами."""
    reviews = Review.objects.select_related("book", "book__genre", "author")

    q = request.GET.get("q", "").strip()
    genre = request.GET.get("genre", "")
    sort = request.GET.get("sort", "new")

    if q:
        # Ищем и по книге, и по автору книги, и по заголовку рецензии.
        reviews = reviews.filter(
            Q(book__title__icontains=q)
            | Q(book__author__icontains=q)
            | Q(title__icontains=q)
        )
    if genre:
        reviews = reviews.filter(book__genre_id=genre)
    if sort == "rating":
        reviews = reviews.order_by("-rating", "-created_at")
    else:
        reviews = reviews.order_by("-created_at")

    # По 5 рецензий на страницу, чтобы лента не растягивалась на километр.
    paginator = Paginator(reviews, 5)
    page = paginator.get_page(request.GET.get("page"))
    page.object_list = mark_my_reactions(page.object_list, request.user)

    return render(request, "reviews/feed.html", {
        "page": page,
        "genres": Genre.objects.all(),
        "q": q,
        "genre": genre,
        "sort": sort,
    })


def signup(request):
    """Регистрация. После неё сразу входим в аккаунт."""
    if request.user.is_authenticated:
        return redirect("feed")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Готово! Теперь можно написать первую рецензию.")
            return redirect("profile", username=user.username)
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def review_add(request):
    """Написать новую рецензию."""
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            # commit=False: в базу пока не сохраняем, сначала допишем автора.
            review = form.save(commit=False)
            review.author = request.user
            review.save()
            messages.success(request, "Рецензия опубликована.")
            return redirect("review_detail", pk=review.pk)
    else:
        form = ReviewForm()
        # Если пришли со страницы книги, сразу выбираем её в списке.
        book_id = request.GET.get("book")
        if book_id and book_id.isdigit():
            form.fields["book"].initial = book_id
    return render(request, "reviews/review_form.html", {
        "form": form, "heading": "Новая рецензия",
    })


def review_detail(request, pk):
    """Одна рецензия целиком."""
    review = get_object_or_404(
        Review.objects.select_related("book", "book__genre", "author"), pk=pk
    )
    mark_my_reactions([review], request.user)
    return render(request, "reviews/review_detail.html", {"review": review})


@login_required
def review_edit(request, pk):
    """Редактировать может только автор: чужую рецензию просто не найдём (404)."""
    review = get_object_or_404(Review, pk=pk, author=request.user)
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Рецензия обновлена.")
            return redirect("review_detail", pk=review.pk)
    else:
        form = ReviewForm(instance=review)
    return render(request, "reviews/review_form.html", {
        "form": form, "heading": "Правим рецензию",
    })


@login_required
def review_delete(request, pk):
    """Удаляем только по кнопке из формы, то есть только через POST."""
    review = get_object_or_404(Review, pk=pk, author=request.user)
    if request.method == "POST":
        review.delete()
        messages.success(request, "Рецензия удалена.")
        return redirect("profile", username=request.user.username)
    return render(request, "reviews/review_confirm_delete.html", {"review": review})


@login_required
def react(request, pk, action):
    """Лайк или дизлайк. Повторное нажатие той же кнопки снимает оценку."""
    if request.method != "POST":
        return redirect("review_detail", pk=pk)
    if action not in ("like", "dislike"):
        return redirect("review_detail", pk=pk)

    review = get_object_or_404(Review, pk=pk)
    value = LIKE if action == "like" else DISLIKE

    # Если реакции ещё не было — создаём. Если была — меняем или удаляем.
    reaction, created = Reaction.objects.get_or_create(
        review=review, user=request.user, defaults={"value": value}
    )
    if not created:
        if reaction.value == value:
            reaction.delete()
        else:
            reaction.value = value
            reaction.save()

    # Возвращаем человека туда, откуда он нажал кнопку.
    # Проверяем адрес, чтобы нельзя было подставить чужой сайт.
    next_url = request.POST.get("next", "")
    if next_url.startswith("/") and not next_url.startswith("//"):
        return redirect(next_url)
    return redirect("review_detail", pk=pk)


@login_required
def book_add(request):
    """Добавить книгу, если её ещё нет в списке."""
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.added_by = request.user
            book.save()
            messages.success(request, "Книга добавлена. Осталось написать рецензию!")
            # Сразу открываем форму рецензии с уже выбранной этой книгой.
            return redirect(f"{reverse('review_add')}?book={book.pk}")
    else:
        form = BookForm()
    return render(request, "reviews/book_form.html", {"form": form})


def book_detail(request, pk):
    """Страница книги: все рецензии про неё."""
    book = get_object_or_404(Book.objects.select_related("genre"), pk=pk)
    reviews = Review.objects.filter(book=book).select_related("author").order_by("-created_at")
    # Здесь рецензий обычно немного, поэтому пагинацию не делали.
    reviews = mark_my_reactions(reviews, request.user)
    return render(request, "reviews/book_detail.html", {"book": book, "reviews": reviews})


def profile(request, username):
    """Чужой или свой профиль: данные, статистика и рецензии человека."""
    person = get_object_or_404(User, username=username)
    person_profile = get_profile(person)
    reviews = Review.objects.filter(author=person).select_related("book").order_by("-created_at")
    reviews = mark_my_reactions(reviews[:20], request.user)

    return render(request, "reviews/profile.html", {
        "person": person,
        "person_profile": person_profile,
        "reviews": reviews,
        "reviews_count": Review.objects.filter(author=person).count(),
        "likes_got": Reaction.objects.filter(review__author=person, value=LIKE).count(),
        "dislikes_got": Reaction.objects.filter(review__author=person, value=DISLIKE).count(),
    })


@login_required
def profile_edit(request):
    """Редактирование своего профиля."""
    person_profile = get_profile(request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=person_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлён.")
            return redirect("profile", username=request.user.username)
    else:
        form = ProfileForm(instance=person_profile)
    return render(request, "reviews/profile_edit.html", {"form": form})
