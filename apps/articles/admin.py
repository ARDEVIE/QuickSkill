# Django modules
from django.contrib import admin

# Project modules
from apps.articles.models import Article, ArticleBlock, Comment, FavoriteArticle


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_at', 'created_at')
    search_fields = ('title', 'content')
    list_filter = ('published_at', 'created_at')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'created_at', 'updated_at')
    search_fields = ('content', 'user__username', 'article__title')
    list_filter = ('created_at',)


admin.site.register(ArticleBlock)
admin.site.register(FavoriteArticle)
