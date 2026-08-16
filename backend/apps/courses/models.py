# Django modules
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import (
    CASCADE,
    SET_NULL,
    BooleanField,
    CharField,
    DateTimeField,
    FileField,
    ForeignKey,
    Model,
    PositiveIntegerField,
    SlugField,
    TextChoices,
    TextField,
    UniqueConstraint,
    URLField,
)

# Project modules
from apps.common.models import TimeStampedModel
from apps.common.utils import unique_slugify


class Category(Model):
    '''A topic used to group and filter courses in the catalog.'''

    name = CharField(max_length=100, unique=True)
    slug = SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name)
        super().save(*args, **kwargs)


class Course(TimeStampedModel):
    '''A mini-course published by its author; visible to others only once is_published.'''

    title = CharField(max_length=200)
    description = TextField(blank=True)
    category = ForeignKey(
        Category,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        related_name='courses',
    )
    author = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name='authored_courses',
    )
    is_published = BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Material(TimeStampedModel):
    '''A single PDF file or video link attached to a course.'''

    class MaterialType(TextChoices):
        PDF = 'pdf', 'PDF'
        VIDEO_LINK = 'video_link', 'Video link'

    course = ForeignKey(Course, on_delete=CASCADE, related_name='materials')
    title = CharField(max_length=200)
    type = CharField(max_length=20, choices=MaterialType.choices)
    file = FileField(upload_to='materials/', blank=True, null=True)
    url = URLField(blank=True)
    order = PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.title

    def clean(self):
        if self.type == self.MaterialType.PDF:
            if not self.file:
                raise ValidationError({'file': 'PDF material must have a file attached.'})
            if self.url:
                raise ValidationError({'url': 'PDF material must not have a URL.'})
        elif self.type == self.MaterialType.VIDEO_LINK:
            if not self.url:
                raise ValidationError({'url': 'Video link material must have a URL.'})
            if self.file:
                raise ValidationError({'file': 'Video link material must not have a file.'})


class Favorite(Model):
    user = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name='favorites',
    )
    course = ForeignKey(Course, on_delete=CASCADE, related_name='favorited_by')
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            UniqueConstraint(fields=['user', 'course'], name='unique_user_course_favorite'),
        ]

    def __str__(self):
        return f'{self.user} -> {self.course}'
