from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path

from arches_component_lab.views.api.card import CardDataView
from arches_component_lab.views.api.relatable_resources import RelatableResourcesView
from arches_component_lab.views.api.widgets import (
    WidgetDataView,
    NodeDataView,
)
from arches_component_lab.views.api.card_x_node_x_widget import (
    CardXNodeXWidgetView,
    CardXNodeXWidgetListFromNodegroupView,
)

from arches_querysets.rest_framework.generic_views import (
    ArchesTileDetailView,
    ArchesTileListCreateView,
)

urlpatterns = [
    path(
        "arches-component-lab/api/relatable-resources/<slug:graph>/<slug:node_alias>",
        RelatableResourcesView.as_view(),
        name="api-relatable-resources",
    ),
    path(
        "arches-component-lab/api/widget-data/<slug:graph_slug>/<slug:node_alias>",
        CardXNodeXWidgetView.as_view(),
        name="api-card-x-node-x-widget",
    ),
    path(
        "arches-component-lab/api/widget-data/<slug:graph_slug>/<slug:node_alias>",
        WidgetDataView.as_view(),
        name="api-widget-data",
    ),
    path(
        "arches-component-lab/api/node-data/<slug:graph_slug>/<slug:node_alias>",
        NodeDataView.as_view(),
        name="api-node-data",
    ),
    path(
        "arches-component-lab/api/card-x-node-x-widget-list-from-nodegroup/<slug:graph_slug>/<slug:nodegroup_alias>",
        CardXNodeXWidgetListFromNodegroupView.as_view(),
        name="api-card-x-node-x-widget-list-from-nodegroup",
    ),
    path(
        "arches-component-lab/api/card-data/<slug:graph_slug>/<slug:nodegroup_alias>",
        CardDataView.as_view(),
        name="api-card-data",
    ),
    path(
        "arches-component-lab/api/tile/<slug:graph>/<slug:nodegroup_alias>/<uuid:pk>",
        ArchesTileDetailView.as_view(),
        name="api-tile",
    ),
    path(
        "arches-component-lab/api/tile/<slug:graph>/<slug:nodegroup_alias>",
        ArchesTileDetailView.as_view(),
        name="api-foo",
    ),
    path(
        "arches-component-lab/api/tile-list-create/<slug:graph>/<slug:nodegroup_alias>/<uuid:pk>",
        ArchesTileListCreateView.as_view(),
        name="api-tile-list-create",
    ),
]

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
