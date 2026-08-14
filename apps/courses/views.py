# Django modules
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

# Project modules
from apps.articles.models import Question
from apps.courses.forms import CourseForm, MaterialForm
from apps.courses.models import Category, Course, Favorite, Material


def catalog_view(request):
    '''Public course catalog; authenticated users also see their own drafts.'''
    courses = Course.objects.select_related('category', 'author')
    user = request.user

    if user.is_authenticated:
        courses = courses.filter(Q(is_published=True) | Q(author=user))
    else:
        courses = courses.filter(is_published=True)

    search = request.GET.get('search', '').strip()
    if search:
        courses = courses.filter(title__icontains=search)

    category_slug = request.GET.get('category', '')
    if category_slug:
        courses = courses.filter(category__slug=category_slug)

    # Only look up questions once a category is picked — this is the "didn't
    # understand the course → ask on the forum" hop, scoped to that topic.
    questions = None
    if category_slug:
        questions = Question.objects.filter(category__slug=category_slug).select_related('author')

    context = {
        'courses': courses.distinct(),
        'categories': Category.objects.all(),
        'search': search,
        'selected_category': category_slug,
        'questions': questions,
    }
    return render(request, 'courses/catalog.html', context)


@login_required
def my_learning_view(request):
    '''Courses the current user has favorited — the student side of the cabinet.'''
    favorites = Favorite.objects.filter(user=request.user).select_related(
        'course', 'course__category', 'course__author'
    )
    context = {'courses': [favorite.course for favorite in favorites]}
    return render(request, 'courses/my_learning.html', context)


@login_required
def teaching_view(request):
    '''Courses the current user has authored — the teacher side of the cabinet.'''
    courses = Course.objects.filter(author=request.user).select_related('category', 'author')
    return render(request, 'courses/teaching.html', {'courses': courses})


def course_detail_view(request, pk):
    course = get_object_or_404(
        Course.objects.select_related('category', 'author').prefetch_related('materials'),
        pk=pk,
    )
    user = request.user
    is_owner = user.is_authenticated and course.author == user

    if not course.is_published and not is_owner:
        raise PermissionDenied('Курс ещё не опубликован.')

    is_favorited = user.is_authenticated and Favorite.objects.filter(
        user=user, course=course
    ).exists()

    context = {
        'course': course,
        'is_owner': is_owner,
        'is_favorited': is_favorited,
    }
    return render(request, 'courses/detail.html', context)


@login_required
def course_create_view(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.author = request.user
            course.save()
            messages.success(request, 'Курс создан.')
            return redirect('courses:course_detail', pk=course.pk)
    else:
        form = CourseForm()

    return render(request, 'courses/course_form.html', {'form': form})


@login_required
def course_edit_view(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if course.author != request.user:
        raise PermissionDenied('Редактировать может только автор курса.')

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Курс обновлён.')
            return redirect('courses:course_detail', pk=course.pk)
    else:
        form = CourseForm(instance=course)

    return render(request, 'courses/course_form.html', {'form': form, 'course': course})


@login_required
def course_delete_view(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if course.author != request.user:
        raise PermissionDenied('Удалить может только автор курса.')

    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Курс удалён.')
        return redirect('courses:catalog')

    return render(request, 'courses/course_confirm_delete.html', {'course': course})


@login_required
@require_POST
def course_favorite_view(request, pk):
    course = get_object_or_404(Course, pk=pk)
    favorite, created = Favorite.objects.get_or_create(user=request.user, course=course)
    if not created:
        favorite.delete()
    return redirect('courses:course_detail', pk=pk)


@login_required
def material_add_view(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if course.author != request.user:
        raise PermissionDenied('Добавлять материалы может только автор курса.')

    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.course = course
            material.save()
            messages.success(request, 'Материал добавлен.')
            return redirect('courses:course_detail', pk=course.pk)
    else:
        form = MaterialForm()

    return render(request, 'courses/material_form.html', {'form': form, 'course': course})


@login_required
@require_POST
def material_delete_view(request, pk):
    material = get_object_or_404(Material.objects.select_related('course'), pk=pk)
    if material.course.author != request.user:
        raise PermissionDenied('Удалить материал может только автор курса.')

    course_pk = material.course_id
    material.delete()
    messages.success(request, 'Материал удалён.')
    return redirect('courses:course_detail', pk=course_pk)
