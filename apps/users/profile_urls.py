# Django modules
from django.urls import path

# Project modules
from apps.users.views import MeAPIView

app_name = 'users_api'

urlpatterns = [
    path('me/', MeAPIView.as_view(), name='me'),
]
