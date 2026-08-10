from decouple import Csv, config

from settings.base import *  #noqa


DEBUG = False
ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='', cast=Csv())
