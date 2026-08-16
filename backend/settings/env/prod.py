# Django modules
from django.core.exceptions import ImproperlyConfigured

# Third-party modules
from decouple import Csv, config

# Project modules
from settings.base import *  # noqa

DEBUG = False
ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='', cast=Csv())

# Content-hashed, compressed static files served straight from Gunicorn by
# WhiteNoiseMiddleware. Requires `manage.py collectstatic` to have run (the
# prod Docker command does this on every start) — that's why this isn't in
# base.py: without a manifest, dev/tests would break resolving {% static %}.
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

if SECRET_KEY == 'default-secret-key':
    raise ImproperlyConfigured('PROJECT_SECRET_KEY must be set via environment in production.')

if DATABASES['default']['PASSWORD'] == 'change-me':
    raise ImproperlyConfigured('POSTGRES_PASSWORD must be set via environment in production.')
