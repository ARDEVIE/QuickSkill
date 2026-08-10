# Django modules
from django.urls import path

# Project modules
from apps.courses import views

app_name = 'courses'

urlpatterns = [
    path('', views.catalog_view, name='catalog'),
    path('courses/create/', views.course_create_view, name='course_create'),
    path('courses/<int:pk>/', views.course_detail_view, name='course_detail'),
    path('courses/<int:pk>/edit/', views.course_edit_view, name='course_edit'),
    path('courses/<int:pk>/delete/', views.course_delete_view, name='course_delete'),
    path('courses/<int:pk>/favorite/', views.course_favorite_view, name='course_favorite'),
    path('courses/<int:pk>/materials/add/', views.material_add_view, name='material_add'),
    path('materials/<int:pk>/delete/', views.material_delete_view, name='material_delete'),
]
