# Django modules
from django.conf import settings
from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    FileField,
    ForeignKey,
    ImageField,
    Model,
    SET_NULL,
    SlugField,
    TextChoices,
    TextField,
    PositiveIntegerField,
    UniqueConstraint,
)
from django.utils.text import slugify

# Project modules
from apps.common.models import TimeStampedModel
from apps.courses.models import Category


class Article(TimeStampedModel):
    '''An article published by a user.'''

    title = CharField(max_length=255)
    slug = SlugField(max_length=255, unique=True, blank=True)
    content = TextField(blank=True)
    excerpt = TextField(blank=True)
    category = ForeignKey(
        Category,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        related_name='articles'
    )
    
    author = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name='articles',
    )
    published_at = DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class ArticleBlock(Model):
    class BlockType(TextChoices):
        TEXT = 'text', 'Text'
        MEDIA = 'media', 'Media'

    article = ForeignKey(Article, on_delete=CASCADE, related_name='blocks')
    block_type = CharField(max_length=10, choices=BlockType.choices)
    content = TextField(blank=True)
    media_file = FileField(upload_to='articles/blocks/', blank=True, null=True)
    order = PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Article Block'
        verbose_name_plural = 'Article Blocks'

    def __str__(self):
        return f'{self.article.title} - Block {self.order} ({self.get_block_type_display()})'


class Comment(TimeStampedModel):
    '''A comment on an article by a registered user.'''

    article = ForeignKey(
        Article,
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
        return f'Comment by {self.user.username} on {self.article.title}'


class FavoriteArticle(Model):
    user = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name='favorite_articles',
    )
    article = ForeignKey(Article, on_delete=CASCADE, related_name='favorited_by')
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            UniqueConstraint(fields=['user', 'article'], name='unique_user_article_favorite'),
        ]

    def __str__(self):
        return f'{self.user} -> {self.article}'
