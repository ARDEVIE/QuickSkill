from decouple import Csv, config
from django.core.exceptions import ImproperlyConfigured

from settings.base import *  #noqa


DEBUG = False
ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='', cast=Csv())

if SECRET_KEY == 'default-secret-key':
    raise ImproperlyConfigured('PROJECT_SECRET_KEY must be set via environment in production.')

if DATABASES['default']['PASSWORD'] == 'change-me':
    raise ImproperlyConfigured('POSTGRES_PASSWORD must be set via environment in production.')
