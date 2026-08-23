# Third-party modules
from rest_framework.routers import DefaultRouter

# Project modules
from apps.courses.api_views import (
    CategoryViewSet,
    CourseViewSet,
    LessonViewSet,
    MaterialViewSet,
    RatingViewSet,
)

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('courses', CourseViewSet, basename='course')
router.register('lessons', LessonViewSet, basename='lesson')
router.register('materials', MaterialViewSet, basename='material')
router.register('ratings', RatingViewSet, basename='rating')

urlpatterns = router.urls
