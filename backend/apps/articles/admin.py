# Django modules
from django.contrib import admin

# Project modules
from apps.articles.models import Comment, CommentVote, FavoriteArticle, Question, QuestionVote


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at')
    search_fields = ('title', 'content')
    list_filter = ('category', 'created_at')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('question', 'user', 'created_at', 'updated_at')
    search_fields = ('content', 'user__username', 'question__title')
    list_filter = ('created_at',)


admin.site.register(FavoriteArticle)
admin.site.register(QuestionVote)
admin.site.register(CommentVote)
