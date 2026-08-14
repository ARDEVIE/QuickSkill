# Django modules
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# Third-party modules
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    # JWT API (consumed by the Angular frontend)
    path('api/auth/', include('apps.users.auth_urls')),
    path('api/users/', include('apps.users.profile_urls')),
    path('api/', include('apps.courses.urls')),
    path('api/', include('apps.articles.urls')),
    # API docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
