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

from django.conf import settings
from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.i18n import patterns
from arches.app.views import concept, entity, main, map, resources, search, config, graph
from arches.app.views.graph import GraphManagerView, GraphSettingsView, GraphDataView, DatatypeTemplateView, CardManagerView, CardView, FormManagerView, FormView, ReportManagerView, ReportEditorView
from arches.app.views.resource import ResourceEditorView, ResourceListView, ResourceData, ResourceReportView
from arches.app.views.tile import TileData

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

uuid_regex = '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'

urlpatterns = [
    url(r'^$', main.index),
    url(r'^index.htm', main.index, name='home'),
    url(r'^auth/', main.auth, name='auth'),
    url(r'^rdm/(?P<conceptid>%s|())$' % uuid_regex , concept.rdm, name='rdm'),
    url(r'^map', map.get_page, name="map"),
    url(r'^geocoder', search.geocode, name="geocoder"),

    url(r'^entities/(?P<entityid>%s)$' % uuid_regex , entity.Entities),
    url(r'^concepts/(?P<conceptid>%s)/manage_parents/$' % uuid_regex, concept.manage_parents, name="concept_manage_parents"),
    url(r'^concepts/(?P<conceptid>%s)/confirm_delete/$' % uuid_regex, concept.confirm_delete, name="confirm_delete"),
    url(r'^concepts/(?P<conceptid>%s|())$' % uuid_regex , concept.concept, name="concept"),
    url(r'^concepts/tree$', concept.concept_tree, name="concept_tree"),
    url(r'^concepts/search$', concept.search, name="concept_search"),
    url(r'^concepts/(?P<conceptid>%s)/from_sparql_endpoint$' % uuid_regex, concept.add_concepts_from_sparql_endpoint, name="from_sparql_endpoint"),
    url(r'^concepts/search_sparql_endpoint$', concept.search_sparql_endpoint_for_concepts, name="search_sparql_endpoint"),
    url(r'^concepts/dropdown', concept.dropdown, name="dropdown"),
    url(r'^concepts/get_pref_label', concept.get_pref_label, name="get_pref_label"),
    url(r'^search$', search.home_page, name="search_home"),
    url(r'^search/terms$', search.search_terms, name="search_terms"),
    url(r'^search/resources$', search.search_results, name="search_results"),
    url(r'^search/export$', search.export_results, name="search_results_export"),
    url(r'^buffer/$', search.buffer, name="buffer"),
    url(r'^resources/(?P<resourcetypeid>[0-9a-zA-Z_.]*)/(?P<form_id>[a-zA-Z_-]*)/(?P<resourceid>%s|())$' % uuid_regex, resources.resource_manager, name="resource_manager"),
    url(r'^resources/related/(?P<resourceid>%s|())$' % uuid_regex, resources.related_resources, name="related_resources"),
    url(r'^resources/history/(?P<resourceid>%s|())$' % uuid_regex, resources.edit_history, name="edit_history"),
    url(r'^resources/layers/(?P<entitytypeid>.*)$', resources.map_layers, name="map_layers"),
    url(r'^resources/markers/(?P<entitytypeid>.*)$', resources.map_layers, {'get_centroids':True}, name="map_markers"),
    url(r'^reports/(?P<resourceid>%s)$' % uuid_regex , resources.report, name='report'),
    url(r'^get_admin_areas', resources.get_admin_areas, name='get_admin_areas'),
    url(r'^config/', config.manager, name='config'),
    url(r'^graph/(?P<graphid>%s|())$' % uuid_regex, GraphManagerView.as_view(), name='graph'),
    url(r'^graph/(?P<graphid>%s)/settings$' % uuid_regex, GraphSettingsView.as_view(), name='graph_settings'),
    url(r'^graph/(?P<graphid>%s)/card_manager$' % uuid_regex, CardManagerView.as_view(), name='card_manager'),
    url(r'^graph/(?P<graphid>%s)/append_branch$' % uuid_regex, GraphDataView.as_view(action='append_branch'), name='append_branch'),
    url(r'^graph/(?P<graphid>%s)/move_node$' % uuid_regex, GraphDataView.as_view(action='move_node'), name='move_node'),
    url(r'^graph/(?P<graphid>%s)/update_node$' % uuid_regex, GraphDataView.as_view(action='update_node'), name='update_node'),
    url(r'^graph/(?P<graphid>%s)/delete_node$' % uuid_regex, GraphDataView.as_view(action='delete_node'), name='delete_node'),
    url(r'^graph/(?P<graphid>%s)/clone$' % uuid_regex, GraphDataView.as_view(action='clone_graph'), name='clone_graph'),
    url(r'^graph/(?P<graphid>%s)/export$' % uuid_regex, GraphDataView.as_view(action='export_graph'), name='export_graph'),
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
    url(r'^resource$', ResourceListView.as_view(), name='resource'),
    url(r'^resource/(?P<resourceid>%s)$' % uuid_regex, ResourceEditorView.as_view(), name='resource_editor'),
    url(r'^resource/(?P<resourceid>%s)/data/(?P<formid>%s)$' % (uuid_regex, uuid_regex), ResourceData.as_view(), name='resource_data'),
    url(r'^report/(?P<resourceid>%s)$' % uuid_regex, ResourceReportView.as_view(), name='resource_report'),
    url(r'^card/(?P<cardid>%s|())$' % uuid_regex, CardView.as_view(), name='card'),
    url(r'^form/(?P<formid>%s|())$' % uuid_regex, FormView.as_view(), name='form'),
    url(r'^form/(?P<formid>%s)/delete$' % uuid_regex, FormView.as_view(), name='delete_form'),
    url(r'^report_editor/(?P<reportid>%s|())$' % uuid_regex, ReportEditorView.as_view(), name='report_editor'),
    url(r'^report_editor/(?P<reportid>%s)/delete$' % uuid_regex, ReportEditorView.as_view(), name='delete_report'),
    url(r'^node/(?P<graphid>%s)$' % uuid_regex, GraphDataView.as_view(action='update_node'), name='node'),
    url(r'^widgets/(?P<template>[a-zA-Z_-]*)', main.widget, name="widgets"),
    url(r'^report-templates/(?P<template>[a-zA-Z_-]*)', main.report_templates, name="report-templates"),
    url(r'^tile', TileData.as_view(), name="tile"),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', admin.site.urls),
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
