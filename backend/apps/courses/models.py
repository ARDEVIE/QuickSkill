# Django modules
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import (
    CASCADE,
    SET_NULL,
    BooleanField,
    CharField,
    DateTimeField,
    FileField,
    ForeignKey,
    ImageField,
    Model,
    PositiveIntegerField,
    PositiveSmallIntegerField,
    SlugField,
    TextChoices,
    TextField,
    UniqueConstraint,
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
    cover = ImageField(upload_to='courses/covers/', blank=True, null=True)
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


class Section(TimeStampedModel):
    '''A structural subsection of a course.'''
    course = ForeignKey(Course, on_delete=CASCADE, related_name='sections')
    title = CharField(max_length=200)
    order = PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class ContentBlock(TimeStampedModel):
    '''A single lesson item inside a section: text, a video link, a generic link, or a file.'''

    class BlockType(TextChoices):
        TEXT = 'text', 'Text'
        VIDEO_LINK = 'video_link', 'Video link'
        LINK = 'link', 'Link'
        MEDIA = 'media', 'Media'

    section = ForeignKey(Section, on_delete=CASCADE, related_name='blocks')
    title = CharField(max_length=200, blank=True)
    type = CharField(max_length=20, choices=BlockType.choices, default=BlockType.TEXT)
    content = TextField(blank=True)  # Used for text content or URL
    file = FileField(upload_to='blocks/media/', blank=True, null=True)
    order = PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Block {self.id} ({self.type}) in {self.section.title}"


class Rating(TimeStampedModel):
    '''A 1-5 review a user leaves on a course; one per user per course.'''

    course = ForeignKey(Course, on_delete=CASCADE, related_name='ratings')
    user = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name='course_ratings',
    )
    score = PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            UniqueConstraint(fields=['user', 'course'], name='unique_user_course_rating'),
        ]

    def __str__(self):
        return f'{self.user} rated {self.course} {self.score}/5'


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
