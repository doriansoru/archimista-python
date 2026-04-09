"""
URL configuration for archimista_python project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django_select2 import urls as select2_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('select2/', include(select2_urls)),
    path('', include('archimista_python.archive.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
