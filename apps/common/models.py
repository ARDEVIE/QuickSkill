# Django modules
from django.db.models import DateTimeField, Model


class TimeStampedModel(Model):
    '''Abstract base adding created_at/updated_at to a model.'''

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True
