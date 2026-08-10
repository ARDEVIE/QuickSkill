# Django modules
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

# Third-party modules
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Session-based Django templates (browser-rendered pages)
    path('', include('apps.courses.urls')),
    path('auth/', include('apps.users.urls')),
    # JWT API (consumed by the React frontend)
    path('api/', include('apps.users.api_urls')),
    path('api/', include('apps.courses.api_urls')),
    # API docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# WhiteNoise serves STATIC_URL. MEDIA (avatars, PDFs) has no S3/Nginx setup yet for
# this MVP, so Django serves it directly regardless of DEBUG — django.conf.urls.static.static()
# refuses to do that (it's a no-op unless DEBUG=True), so this uses the underlying
# view directly. Move to S3 or an Nginx volume mount before real user traffic —
# this doesn't scale past a demo.
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
