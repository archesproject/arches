from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^', include('arches.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
