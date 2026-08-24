# Third-party modules
from rest_framework.routers import DefaultRouter

# Project modules
from apps.courses.api_views import (
    CategoryViewSet,
    ContentBlockViewSet,
    CourseViewSet,
    RatingViewSet,
    ResourceViewSet,
    SectionViewSet,
)

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('courses', CourseViewSet, basename='course')
router.register('sections', SectionViewSet, basename='section')
router.register('blocks', ContentBlockViewSet, basename='block')
router.register('ratings', RatingViewSet, basename='rating')
router.register('resources', ResourceViewSet, basename='resource')

urlpatterns = router.urls
