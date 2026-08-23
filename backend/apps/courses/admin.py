# Django modules
from django.contrib import admin

# Project modules
from apps.courses.models import Category, ContentBlock, Course, Favorite, Rating, Section


class SectionInline(admin.TabularInline):
    model = Section
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_published', 'created_at')
    list_filter = ('is_published', 'category')
    search_fields = ('title', 'author__username', 'author__email')
    inlines = [SectionInline]


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    search_fields = ('title', 'course__title')


@admin.register(ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    list_display = ('id', 'section', 'type', 'order')
    list_filter = ('type',)
    search_fields = ('section__title',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'created_at')
    search_fields = ('user__username', 'course__title')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('course', 'user', 'score', 'created_at')
    list_filter = ('score',)
    search_fields = ('course__title', 'user__username')
