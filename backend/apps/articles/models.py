# Django modules
from django.conf import settings
from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    FileField,
    ForeignKey,
    Model,
    SET_NULL,
    SlugField,
    TextField,
    UniqueConstraint,
)

# Project modules
from apps.common.models import TimeStampedModel
from apps.common.utils import unique_slugify
from apps.courses.models import Category


class Question(TimeStampedModel):
    '''A question asked by a user on the forum, scoped to a course category.'''

    title = CharField(max_length=255)
    slug = SlugField(max_length=255, unique=True, blank=True)
    content = TextField(blank=True)
    media_file = FileField(upload_to='forum/questions/', blank=True, null=True)
    category = ForeignKey(
        Category,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        related_name='questions'
    )

    author = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name='questions',
    )
    accepted_comment = ForeignKey(
        'Comment',
        on_delete=SET_NULL,
        null=True,
        blank=True,
        related_name='accepted_for',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)


class Comment(TimeStampedModel):
    '''A comment (answer) on a question by a registered user.'''

    question = ForeignKey(
        Question,
        on_delete=CASCADE,
        related_name='comments',
    )
    user = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name='comments',
    )
    content = TextField()
    media_file = FileField(upload_to='comments/media/', blank=True, null=True)
    parent = ForeignKey(
        'self',
        on_delete=CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self):
        return f'Comment by {self.user.username} on {self.question.title}'


class FavoriteArticle(Model):
    user = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name='favorite_articles',
    )
    question = ForeignKey(Question, on_delete=CASCADE, related_name='favorited_by')
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            UniqueConstraint(fields=['user', 'question'], name='unique_user_question_favorite'),
        ]

    def __str__(self):
        return f'{self.user} -> {self.question}'
