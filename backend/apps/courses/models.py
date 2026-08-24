# Django modules
from django.conf import settings
from django.core.exceptions import ValidationError
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


class Lesson(TimeStampedModel):
    '''A named topic within a course that groups a set of materials.'''

    course = ForeignKey(Course, on_delete=CASCADE, related_name='lessons')
    title = CharField(max_length=200)
    description = TextField(blank=True)
    order = PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.title


class Material(TimeStampedModel):
    '''A single piece of course content: a PDF, a video link, a plain link, or text.'''

    class MaterialType(TextChoices):
        PDF = 'pdf', 'PDF'
        VIDEO_LINK = 'video_link', 'Video link'
        LINK = 'link', 'Link'
        TEXT = 'text', 'Text'

    course = ForeignKey(Course, on_delete=CASCADE, related_name='materials')
    lesson = ForeignKey(
        Lesson,
        on_delete=CASCADE,
        related_name='materials',
        null=True,
        blank=True,
    )
    title = CharField(max_length=200)
    type = CharField(max_length=20, choices=MaterialType.choices)
    file = FileField(upload_to='materials/', blank=True, null=True)
    url = URLField(blank=True)
    content = TextField(blank=True)
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
        elif self.type in (self.MaterialType.VIDEO_LINK, self.MaterialType.LINK):
            if not self.url:
                raise ValidationError({'url': f'{self.get_type_display()} material must have a URL.'})
            if self.file:
                raise ValidationError({'file': f'{self.get_type_display()} material must not have a file.'})
        elif self.type == self.MaterialType.TEXT:
            if not self.content:
                raise ValidationError({'content': 'Text material must have content.'})


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
