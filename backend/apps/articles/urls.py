# Third-party modules
from rest_framework.routers import DefaultRouter

# Project modules
from apps.articles import views

router = DefaultRouter()
router.register('questions', views.QuestionViewSet, basename='question')
router.register('comments', views.CommentViewSet, basename='comment')

urlpatterns = router.urls
