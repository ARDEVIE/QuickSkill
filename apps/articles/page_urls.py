# Django modules
from django.urls import path

# Project modules
from apps.articles import page_views

app_name = 'articles_page'

urlpatterns = [
    path('', page_views.article_list_page, name='list_page'),
    path('create/', page_views.article_create_page, name='create_page'),
    path('<slug:slug>/edit/', page_views.article_edit_page, name='edit_page'),
    path('<slug:slug>/', page_views.article_test_page, name='test_page'),
]
