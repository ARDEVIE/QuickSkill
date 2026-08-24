# Django modules
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import (
    CASCADE,
    CharField,
    CheckConstraint,
    DateTimeField,
    FileField,
    ForeignKey,
    Model,
    Q,
    SET_NULL,
    SlugField,
    SmallIntegerField,
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
    tags = CharField(max_length=200, blank=True)  # comma-separated, freeform
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


class QuestionVote(Model):
    '''A user's up/down vote on a question; one vote per user per question.'''

    question = ForeignKey(Question, on_delete=CASCADE, related_name='votes')
    user = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name='question_votes',
    )
    value = SmallIntegerField(validators=[MinValueValidator(-1), MaxValueValidator(1)])
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'question'], name='unique_user_question_vote'),
            CheckConstraint(condition=Q(value__in=[-1, 1]), name='question_vote_value_is_plus_or_minus_one'),
        ]

    def __str__(self):
        return f'{self.user} -> {self.question} ({self.value:+d})'


class CommentVote(Model):
    '''A user's up/down vote on an answer (comment); one vote per user per comment.'''

    comment = ForeignKey(Comment, on_delete=CASCADE, related_name='votes')
    user = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name='comment_votes',
    )
    value = SmallIntegerField(validators=[MinValueValidator(-1), MaxValueValidator(1)])
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'comment'], name='unique_user_comment_vote'),
            CheckConstraint(condition=Q(value__in=[-1, 1]), name='comment_vote_value_is_plus_or_minus_one'),
        ]

    def __str__(self):
        return f'{self.user} -> comment {self.comment_id} ({self.value:+d})'


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
