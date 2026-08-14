# Django modules
from django.urls import path

# Third-party modules
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Project modules
from apps.users.api_views import LogoutAPIView, MeAPIView, RegisterAPIView

app_name = 'users_api'

urlpatterns = [
    path('auth/register/', RegisterAPIView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('auth/logout/', LogoutAPIView.as_view(), name='logout'),
    path('users/me/', MeAPIView.as_view(), name='me'),
]
