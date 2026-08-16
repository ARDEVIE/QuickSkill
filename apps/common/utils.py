# Django modules
from django.utils.text import slugify


def unique_slugify(instance, value, slug_field='slug'):
    '''Slugify `value` for `instance`, appending -2, -3... on collision.

    Plain slugify() drops non-ASCII characters entirely, so a Cyrillic-only
    title collapses to an empty string — allow_unicode keeps it usable.
    '''
    base_slug = slugify(value, allow_unicode=True) or 'item'
    slug = base_slug
    model = type(instance)
    suffix = 2

    while model.objects.filter(**{slug_field: slug}).exclude(pk=instance.pk).exists():
        slug = f'{base_slug}-{suffix}'
        suffix += 1

    return slug
