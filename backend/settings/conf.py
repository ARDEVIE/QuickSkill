# Python modules
from datetime import timedelta

# Third-party modules
from decouple import Csv, config

SECRET_KEY = config('PROJECT_SECRET_KEY', default='default-secret-key', cast=str)
ENV_ID = config('PROJECT_ENV_ID', default='dev', cast=str)
ALLOWED_ENV_ID = ('dev', 'prod')

if ENV_ID not in ALLOWED_ENV_ID:
    raise ValueError(f'Invalid ENV_ID: {ENV_ID}. Allowed values are {ALLOWED_ENV_ID}')


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
    'DEFAULT_PAGINATION_CLASS': 'apps.common.pagination.DefaultPagination',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    }
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'QuickSkill API',
    'DESCRIPTION': 'Auth, courses and materials API for the QuickSkill MVP.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:4200,http://127.0.0.1:4200', cast=Csv())
