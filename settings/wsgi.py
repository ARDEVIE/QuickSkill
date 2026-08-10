# Python modules
import os

# Django modules
from django.core.wsgi import get_wsgi_application

# Project modules
from settings.conf import ENV_ID

os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'settings.env.{ENV_ID}')

application = get_wsgi_application()
