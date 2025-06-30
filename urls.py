from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path

from arches_querysets.apps import ArchesQuerySetsConfig
from arches_querysets.rest_framework.generic_views import (
    ArchesResourceDetailView,
    ArchesResourceListCreateView,
    ArchesTileDetailView,
    ArchesTileListCreateView,
)

app_name = ArchesQuerySetsConfig.name
arches_rest_framework_urls = [
    path(
        "api/resource/<slug:graph>",
        ArchesResourceListCreateView.as_view(),
        name="api-resources",
    ),
    path(
        "api/resource/<slug:graph>/<uuid:pk>",
        ArchesResourceDetailView.as_view(),
        name="api-resource",
    ),
    path(
        "api/tile/<slug:graph>/<slug:nodegroup_alias>",
        ArchesTileListCreateView.as_view(),
        name="api-tiles",
    ),
    path(
        "api/tile/<slug:graph>/<slug:nodegroup_alias>/<uuid:pk>",
        ArchesTileDetailView.as_view(),
        name="api-tile",
    ),
]

urlpatterns = [
    *arches_rest_framework_urls,
]

# handler400 = "arches.app.views.main.custom_400"
# handler403 = "arches.app.views.main.custom_403"
# handler404 = "arches.app.views.main.custom_404"
# handler500 = "arches.app.views.main.custom_500"

# Ensure Arches core urls are superseded by project-level urls
urlpatterns.append(path("", include("arches.urls")))

# Adds URL pattern to serve media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Only handle i18n routing in active project. This will still handle the routes provided by Arches core and Arches applications,
# but handling i18n routes in multiple places causes application errors.
if settings.ROOT_URLCONF == __name__:
    if settings.SHOW_LANGUAGE_SWITCH is True:
        urlpatterns = i18n_patterns(*urlpatterns)

    urlpatterns.append(path("i18n/", include("django.conf.urls.i18n")))
