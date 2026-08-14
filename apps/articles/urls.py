# Third-party modules
from rest_framework.routers import DefaultRouter

# Project modules
from apps.articles import views

router = DefaultRouter()
router.register('articles', views.ArticleViewSet, basename='article')
router.register('comments', views.CommentViewSet, basename='comment')
router.register('article-blocks', views.ArticleBlockViewSet, basename='article-block')

urlpatterns = router.urls
