from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from apps.users import views


app_name = "users"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit_view, name="profile_edit"),
    path("settings/", views.settings_view, name="settings"),
    path("theme/", views.set_theme_view, name="set_theme"),
]
