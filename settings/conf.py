from decouple import config


SECRET_KEY = config('PROJECT_SECRET_KEY', default='default-secret-key', cast=str)
ENV_ID = config('PROJECT_ENV_ID', default='dev', cast=str)
ALLOWED_ENV_ID = ('dev', 'prod')