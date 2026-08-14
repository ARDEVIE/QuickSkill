# Django modules
from django.urls import path

# Third-party modules
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Project modules
from apps.users.views import LogoutAPIView, RegisterAPIView

app_name = 'auth_api'

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
]
