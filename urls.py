from django.urls import path

from arches_querysets.apps import ArchesQuerySetsConfig
from arches_querysets.rest_framework.generic_views import (
    ArchesResourceBlankView,
    ArchesResourceDetailView,
    ArchesResourceListCreateView,
    ArchesTileBlankView,
    ArchesTileDetailView,
    ArchesTileListCreateView,
)

app_name = ArchesQuerySetsConfig.name
urlpatterns = [
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
        "api/resource/<slug:graph>/blank",
        ArchesResourceBlankView.as_view(),
        name="api-resource-blank",
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
    path(
        "api/tile/<slug:graph>/<slug:nodegroup_alias>/blank",
        ArchesTileBlankView.as_view(),
        name="api-tile-blank",
    ),
]
