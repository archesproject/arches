'''
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.i18n import patterns
from arches.app.views import concept, entity, main, map, resources, search, config, graph, tileserver
from arches.app.views.admin import ReIndexResources
from arches.app.views.graph import GraphManagerView, GraphSettingsView, GraphDataView, DatatypeTemplateView, CardManagerView, CardView, FormManagerView, FormView, ReportManagerView, ReportEditorView, FunctionManagerView, PermissionManagerView, PermissionDataView
from arches.app.views.resource import ResourceEditorView, ResourceListView, ResourceData, ResourceReportView, RelatedResourcesView, ResourceDescriptors
from arches.app.views.concept import RDMView
from arches.app.views.tile import TileData
from arches.app.views.map import MapLayerManagerView
from arches.app.models.system_settings import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

uuid_regex = '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'

urlpatterns = [
    url(r'^$', main.index),
    url(r'^index.htm', main.index, name='home'),
    url(r'^auth/', main.auth, name='auth'),
    url(r'^rdm/(?P<conceptid>%s|())$' % uuid_regex , RDMView.as_view(), name='rdm'),
    url(r'^geocoder', search.geocode, name="geocoder"),

    url(r'^admin/reindex/resources$', ReIndexResources.as_view(), name="reindex"),
    url(r'^entities/(?P<entityid>%s)$' % uuid_regex , entity.Entities),
    url(r'^concepts/(?P<conceptid>%s)/manage_parents/$' % uuid_regex, concept.manage_parents, name="concept_manage_parents"),
    url(r'^concepts/(?P<conceptid>%s)/confirm_delete/$' % uuid_regex, concept.confirm_delete, name="confirm_delete"),
    url(r'^concepts/(?P<conceptid>%s|())$' % uuid_regex , concept.concept, name="concept"),
    url(r'^concepts/tree/(?P<mode>.*)', concept.concept_tree, name="concept_tree"),
    url(r'^concepts/search$', concept.search, name="concept_search"),
    url(r'^concepts/(?P<conceptid>%s)/from_sparql_endpoint$' % uuid_regex, concept.add_concepts_from_sparql_endpoint, name="from_sparql_endpoint"),
    url(r'^concepts/search_sparql_endpoint$', concept.search_sparql_endpoint_for_concepts, name="search_sparql_endpoint"),
    url(r'^concepts/dropdown', concept.dropdown, name="dropdown"),
    url(r'^concepts/export/(?P<conceptid>%s)$' % uuid_regex , concept.export, name="export_concept"),
    url(r'^concepts/export/collections', concept.export_collections, name="export_concept_collections"),
    url(r'^concepts/get_pref_label', concept.get_pref_label, name="get_pref_label"),
    url(r'^conceptvalue/', concept.concept_value, name="concept_value"),
    url(r'^search$', search.SearchView.as_view(), name="search_home"),
    url(r'^search/terms$', search.search_terms, name="search_terms"),
    url(r'^search/resources$', search.search_results, name="search_results"),
    url(r'^search/export$', search.export_results, name="search_results_export"),
    url(r'^search/time_wheel_config$', search.time_wheel_config, name="time_wheel_config"),
    url(r'^buffer/$', search.buffer, name="buffer"),
    url(r'^resources/(?P<resourcetypeid>[0-9a-zA-Z_.]*)/(?P<form_id>[a-zA-Z_-]*)/(?P<resourceid>%s|())$' % uuid_regex, resources.resource_manager, name="resource_manager"),
    url(r'^resources/history/(?P<resourceid>%s|())$' % uuid_regex, resources.edit_history, name="edit_history"),
    url(r'^resources/layers/(?P<entitytypeid>.*)$', resources.map_layers, name="map_layers"),
    url(r'^resources/markers/(?P<entitytypeid>.*)$', resources.map_layers, {'get_centroids':True}, name="map_markers"),
    url(r'^reports/(?P<resourceid>%s)$' % uuid_regex , resources.report, name='report'),
    url(r'^get_admin_areas', resources.get_admin_areas, name='get_admin_areas'),
    url(r'^settings/', ResourceEditorView.as_view(), { 'resourceid': settings.RESOURCE_INSTANCE_ID, 'view_template':'views/system-settings.htm', 'main_script':'views/system-settings', 'nav_menu':False}, name='config'),
    url(r'^graph/(?P<graphid>%s|())$' % uuid_regex, GraphManagerView.as_view(), name='graph'),
    url(r'^graph/(?P<graphid>%s)/settings$' % uuid_regex, GraphSettingsView.as_view(), name='graph_settings'),
    url(r'^graph/(?P<graphid>%s)/card_manager$' % uuid_regex, CardManagerView.as_view(), name='card_manager'),
    url(r'^graph/(?P<graphid>%s)/append_branch$' % uuid_regex, GraphDataView.as_view(action='append_branch'), name='append_branch'),
    url(r'^graph/(?P<graphid>%s)/move_node$' % uuid_regex, GraphDataView.as_view(action='move_node'), name='move_node'),
    url(r'^graph/(?P<graphid>%s)/update_node$' % uuid_regex, GraphDataView.as_view(action='update_node'), name='update_node'),
    url(r'^graph/(?P<graphid>%s)/delete_node$' % uuid_regex, GraphDataView.as_view(action='delete_node'), name='delete_node'),
    url(r'^graph/(?P<graphid>%s)/clone$' % uuid_regex, GraphDataView.as_view(action='clone_graph'), name='clone_graph'),
    url(r'^graph/(?P<graphid>%s)/export$' % uuid_regex, GraphDataView.as_view(action='export_graph'), name='export_graph'),
    url(r'^graph/(?P<graphid>%s)/export_mapping_file$' % uuid_regex, GraphDataView.as_view(action='export_mapping_file'), name='export_mapping_file'),
    url(r'^graph/import/', GraphDataView.as_view(action='import_graph'), name='import_graph'),
    url(r'^graph/datatypes/(?P<template>[a-zA-Z_-]*)', DatatypeTemplateView.as_view(), name='datatype_template'),
    url(r'^graph/new$', GraphDataView.as_view(action='new_graph'), name='new_graph'),
    url(r'^graph/(?P<graphid>%s)/get_related_nodes/(?P<nodeid>%s)$' % (uuid_regex, uuid_regex), GraphDataView.as_view(action='get_related_nodes'), name='get_related_nodes'),
    url(r'^graph/(?P<graphid>%s)/get_valid_domain_nodes/(?P<nodeid>%s)$' % (uuid_regex, uuid_regex), GraphDataView.as_view(action='get_valid_domain_nodes'), name='get_valid_domain_nodes'),
    url(r'^graph/(?P<graphid>%s)/form_manager$' % uuid_regex, FormManagerView.as_view(), name='form_manager'),
    url(r'^graph/(?P<graphid>%s)/add_form$' % uuid_regex, FormManagerView.as_view(action='add_form'), name='add_form'),
    url(r'^graph/(?P<graphid>%s)/reorder_forms$' % uuid_regex, FormManagerView.as_view(action='reorder_forms'), name='reorder_forms'),
    url(r'^graph/(?P<graphid>%s)/report_manager$' % uuid_regex, ReportManagerView.as_view(), name='report_manager'),
    url(r'^graph/(?P<graphid>%s)/add_report$' % uuid_regex, ReportManagerView.as_view(), name='add_report'),
    url(r'^graph/(?P<graphid>%s)/add_resource$' % uuid_regex, ResourceEditorView.as_view(), name='add_resource'),
    url(r'^graph/(?P<graphid>%s)/function_manager$' % uuid_regex, FunctionManagerView.as_view(), name='function_manager'),
    url(r'^graph/(?P<graphid>%s)/apply_functions$' % uuid_regex, FunctionManagerView.as_view(), name='apply_functions'),
    url(r'^graph/(?P<graphid>%s)/remove_functions$' % uuid_regex, FunctionManagerView.as_view(), name='remove_functions'),
    url(r'^graph/(?P<graphid>%s)/permissions$' % uuid_regex, PermissionManagerView.as_view(), name='permission_manager'),
    url(r'^graph/permissions$', PermissionDataView.as_view(), name='permission_data'),
    url(r'^resource$', ResourceListView.as_view(), name='resource'),
    url(r'^resource/(?P<resourceid>%s)$' % uuid_regex, ResourceEditorView.as_view(), name='resource_editor'),
    url(r'^resource/(?P<resourceid>%s)/data/(?P<formid>%s)$' % (uuid_regex, uuid_regex), ResourceData.as_view(), name='resource_data'),
    url(r'^resource/related/(?P<resourceid>%s|())$' % uuid_regex, RelatedResourcesView.as_view(), name="related_resources"),
    url(r'^resource/descriptors/(?P<resourceid>%s|())$' % uuid_regex, ResourceDescriptors.as_view(), name="resource_descriptors"),
    url(r'^report/(?P<resourceid>%s)$' % uuid_regex, ResourceReportView.as_view(), name='resource_report'),
    url(r'^card/(?P<cardid>%s|())$' % uuid_regex, CardView.as_view(), name='card'),
    url(r'^form/(?P<formid>%s|())$' % uuid_regex, FormView.as_view(), name='form'),
    url(r'^form/(?P<formid>%s)/delete$' % uuid_regex, FormView.as_view(), name='delete_form'),
    url(r'^report_editor/(?P<reportid>%s|())$' % uuid_regex, ReportEditorView.as_view(), name='report_editor'),
    url(r'^report_editor/(?P<reportid>%s)/delete$' % uuid_regex, ReportEditorView.as_view(), name='delete_report'),
    url(r'^node/(?P<graphid>%s)$' % uuid_regex, GraphDataView.as_view(action='update_node'), name='node'),
    url(r'^widgets/(?P<template>[a-zA-Z_-]*)', main.widget, name="widgets"),
    url(r'^report-templates/(?P<template>[a-zA-Z_-]*)', main.report_templates, name="report-templates"),
    url(r'^function-templates/(?P<template>[a-zA-Z_-]*)', main.function_templates, name="function-templates"),
    url(r'^tile$', TileData.as_view(action='update_tile'), name="tile"),
    url(r'^tiles/reorder_tiles$', TileData.as_view(action='reorder_tiles'), name='reorder_tiles'),
    url(r'^templates/(?P<template>[a-zA-Z_\-./]*)', main.templates, name="templates"),
    url(r'^tileserver/*', tileserver.handle_request, name="tileserver"),
    url(r'^map_layer_manager/(?P<maplayerid>%s)$' % uuid_regex, MapLayerManagerView.as_view(), name='map_layer_update'),
    url(r'^map_layer_manager/*', MapLayerManagerView.as_view(), name="map_layer_manager"),


    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', admin.site.urls),
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
