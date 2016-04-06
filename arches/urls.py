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
    url(r'^graph/(?P<nodeid>%s)$' % uuid_regex, graph.manager, name='graph'),
    url(r'^graph/append_branch/(?P<nodeid>%s)/(?P<property>[0-9a-zA-Z_-]*)/(?P<branchmetadataid>%s)$' % (uuid_regex, uuid_regex), graph.append_branch, name='append_branch'),
    url(r'^node/(?P<nodeid>%s)$' % uuid_regex, graph.node, name='node'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', admin.site.urls),
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
