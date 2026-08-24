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
    '''A university subject (or general topic) that groups courses, questions and resources.

    Deliberately one model, not two: this is also the catalog/forum "category" filter.
    '''

    name = CharField(max_length=100, unique=True)
    slug = SlugField(max_length=120, unique=True, blank=True)
    code = CharField(max_length=20, blank=True)  # e.g. "CSCI 2105"
    description = TextField(blank=True)

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


class LessonProgress(Model):
    '''Marks that a user has completed a given lesson (content block).'''

    user = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name='lesson_progress',
    )
    block = ForeignKey(ContentBlock, on_delete=CASCADE, related_name='completions')
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'block'], name='unique_user_block_progress'),
        ]

    def __str__(self):
        return f'{self.user} completed {self.block}'


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


class CategoryFollow(Model):
    '''A user following (subscribing to) a subject.'''

    user = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name='followed_categories',
    )
    category = ForeignKey(Category, on_delete=CASCADE, related_name='followers')
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'category'], name='unique_user_category_follow'),
        ]

    def __str__(self):
        return f'{self.user} follows {self.category}'


class Resource(TimeStampedModel):
    '''A loose, subject-scoped material — a PDF, cheat sheet, link, etc. — not tied to any course.'''

    class ResourceType(TextChoices):
        PDF = 'pdf', 'PDF'
        DOCUMENT = 'document', 'Document'
        IMAGE = 'image', 'Image'
        NOTES = 'notes', 'Lecture notes'
        CHEATSHEET = 'cheatsheet', 'Cheat sheet'
        PAST_PAPER = 'past_paper', 'Past paper'
        LINK = 'link', 'Link'
        VIDEO = 'video', 'Video'

    category = ForeignKey(Category, on_delete=CASCADE, related_name='resources')
    author = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name='resources',
    )
    title = CharField(max_length=200)
    description = TextField(blank=True)
    type = CharField(max_length=20, choices=ResourceType.choices)
    url = CharField(max_length=500, blank=True)
    file = FileField(upload_to='resources/', blank=True, null=True)
    tags = CharField(max_length=200, blank=True)  # comma-separated, from a fixed client-side set

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.type})'
