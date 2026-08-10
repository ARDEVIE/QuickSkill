# Third-party modules
from rest_framework.routers import DefaultRouter

# Project modules
from apps.courses.views import CategoryViewSet, CourseViewSet, MaterialViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('courses', CourseViewSet, basename='course')
router.register('materials', MaterialViewSet, basename='material')

urlpatterns = router.urls
