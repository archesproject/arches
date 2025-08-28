from django.urls import path

from arches_component_lab.apps import ArchesComponentLabConfig
from arches_component_lab.views.api.language import LanguageViewWithRequestLanguage
from arches_component_lab.views.api.relatable_resources import RelatableResourcesView
from arches_component_lab.views.api.card_x_node_x_widget import (
    CardXNodeXWidgetView,
    CardXNodeXWidgetListFromNodegroupView,
)
from arches_component_lab.views.api.concept import ConceptsTreeView

from arches_querysets.rest_framework.generic_views import (
    ArchesTileBlankView,
    ArchesTileDetailView,
    ArchesTileListCreateView,
)

app_name = ArchesComponentLabConfig.name

urlpatterns = [
    path(
        "api/languages-with-request-language",
        LanguageViewWithRequestLanguage.as_view(),
        name="api-languages-with-request-language",
    ),
    path(
        "api/relatable-resources/<slug:graph>/<slug:node_alias>",
        RelatableResourcesView.as_view(),
        name="api-relatable-resources",
    ),
    path(
        "api/card-x-node-x-widget-data/<slug:graph_slug>/<slug:node_alias>",
        CardXNodeXWidgetView.as_view(),
        name="api-card-x-node-x-widget",
    ),
    path(
        "api/card-x-node-x-widget-list-from-nodegroup/<slug:graph_slug>/<slug:nodegroup_alias>",
        CardXNodeXWidgetListFromNodegroupView.as_view(),
        name="api-card-x-node-x-widget-list-from-nodegroup",
    ),
    path(
        "api/concepts/<slug:graph_slug>/<slug:node_alias>",
        ConceptsTreeView.as_view(),
        name="api-concepts-tree",
    ),
    path(
        "api/tile/<slug:graph>/<slug:nodegroup_alias>/blank",
        ArchesTileBlankView.as_view(),
        name="api-tile-blank",
    ),
    path(
        "api/tile/<slug:graph>/<slug:nodegroup_alias>/<uuid:pk>",
        ArchesTileDetailView.as_view(),
        name="api-tile",
    ),
    path(
        "api/tile-list-create/<slug:graph>/<slug:nodegroup_alias>/<uuid:pk>",
        ArchesTileListCreateView.as_view(),
        name="api-tile-list-create",
    ),
]
