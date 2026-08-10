from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from apps.users.forms import UserProfileForm, UserRegistrationForm, UserSettingsForm
from apps.users.models import UserSettings


def register_view(request):
    if request.user.is_authenticated:
        return redirect("users:profile")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("users:profile")
    else:
        form = UserRegistrationForm()

    return render(request, "users/register.html", {"form": form})


@login_required
def profile_view(request):
    user_settings, _ = UserSettings.objects.get_or_create(user=request.user)
    authored_courses = request.user.authored_courses.select_related("category")
    favorites = request.user.favorites.select_related("course")

    context = {
        "user_settings": user_settings,
        "authored_courses": authored_courses,
        "favorites": favorites,
    }
    return render(request, "users/profile.html", context)


@login_required
def profile_edit_view(request):
    if request.method == "POST":
        form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=request.user,
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлён.")
            return redirect("users:profile")
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, "users/profile_edit.html", {"form": form})


@login_required
def settings_view(request):
    user_settings, _ = UserSettings.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserSettingsForm(request.POST, instance=user_settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Настройки сохранены.")
            return redirect("users:profile")
    else:
        form = UserSettingsForm(instance=user_settings)

    return render(request, "users/settings.html", {"form": form})


@login_required
@require_POST
def set_theme_view(request):
    theme = request.POST.get("theme")

    if theme not in dict(UserSettings.ThemeChoices.choices):
        return JsonResponse({"ok": False, "error": "Invalid theme."}, status=400)

    user_settings, _ = UserSettings.objects.get_or_create(user=request.user)
    user_settings.theme = theme
    user_settings.save(update_fields=["theme", "updated_at"])

    return JsonResponse({"ok": True, "theme": theme})
