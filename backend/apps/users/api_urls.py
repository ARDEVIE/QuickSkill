# Django modules
from django.urls import path

# Third-party modules
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Project modules
from apps.users.views import LogoutAPIView, MeAPIView, RegisterAPIView
from apps.users.password_reset_views import PasswordResetRequestAPIView, PasswordResetConfirmAPIView

app_name = 'users_api'

urlpatterns = [
    path('auth/register/', RegisterAPIView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('auth/logout/', LogoutAPIView.as_view(), name='logout'),
    path('auth/password-reset/', PasswordResetRequestAPIView.as_view(), name='password_reset'),
    path('auth/password-reset-confirm/', PasswordResetConfirmAPIView.as_view(), name='password_reset_confirm'),
    path('users/me/', MeAPIView.as_view(), name='me'),
]
