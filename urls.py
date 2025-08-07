from django.urls import path

from arches_component_lab.views.api.relatable_resources import RelatableResourcesView
from arches_component_lab.views.api.card_x_node_x_widget import (
    CardXNodeXWidgetView,
    CardXNodeXWidgetListFromNodegroupView,
)

from arches_querysets.rest_framework.generic_views import (
    ArchesTileBlankView,
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
        "arches-component-lab/api/card-x-node-x-widget-data/<slug:graph_slug>/<slug:node_alias>",
        CardXNodeXWidgetView.as_view(),
        name="api-card-x-node-x-widget",
    ),
    path(
        "arches-component-lab/api/card-x-node-x-widget-list-from-nodegroup/<slug:graph_slug>/<slug:nodegroup_alias>",
        CardXNodeXWidgetListFromNodegroupView.as_view(),
        name="api-card-x-node-x-widget-list-from-nodegroup",
    ),
    path(
        "arches-component-lab/api/tile/<slug:graph>/<slug:nodegroup_alias>/blank",
        ArchesTileBlankView.as_view(),
        name="api-tile-blank",
    ),
    path(
        "arches-component-lab/api/tile/<slug:graph>/<slug:nodegroup_alias>/<uuid:pk>",
        ArchesTileDetailView.as_view(),
        name="api-tile",
    ),
    path(
        "arches-component-lab/api/tile-list-create/<slug:graph>/<slug:nodegroup_alias>/<uuid:pk>",
        ArchesTileListCreateView.as_view(),
        name="api-tile-list-create",
    ),
]
