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

from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.i18n import patterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

uuid_regex = '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'

urlpatterns = patterns('',
    url(r'^$', 'arches.app.views.main.index'),
    url(r'^index.htm', 'arches.app.views.main.index', name='home'),
    url(r'^auth/', 'arches.app.views.main.auth', name='auth'),
    url(r'^rdm/(?P<conceptid>%s|())$' % uuid_regex , 'arches.app.views.concept.rdm', name='rdm'),
    url(r'^map', 'arches.app.views.map.get_page', name="map"),
    url(r'^geocoder', 'arches.app.views.search.geocode', name="geocoder"),
    
    url(r'^entities/(?P<entityid>%s)$' % uuid_regex , 'arches.app.views.entity.Entities'),
    url(r'^entityTypes/(?P<entitytypeid>.*)$', 'arches.app.views.entity.EntityTypes'),
    url(r'^concepts/(?P<conceptid>%s)/manage_parents/$' % uuid_regex, 'arches.app.views.concept.manage_parents', name="concept_manage_parents"),        
    url(r'^concepts/(?P<conceptid>%s)/confirm_delete/$' % uuid_regex, 'arches.app.views.concept.confirm_delete', name="confirm_delete"),     
    url(r'^concepts/(?P<conceptid>%s|())/$' % uuid_regex , 'arches.app.views.concept.concept', name="concept"),
    url(r'^concepts/tree', 'arches.app.views.concept.concept_tree', name="concept_tree"),      
    url(r'^concepts/search', 'arches.app.views.concept.search', name="concept_search"),
    url(r'^search$', 'arches.app.views.search.home_page', name="search_home"),
    url(r'^search/terms$', 'arches.app.views.search.search_terms', name="search_terms"),
    url(r'^search/resources$', 'arches.app.views.search.search_results', name="search_results"),
    url(r'^search/export$', 'arches.app.views.search.export_results', name="search_results_export"),
    url(r'^buffer/$', 'arches.app.views.search.buffer', name="buffer"),
    url(r'^resources/(?P<resourcetypeid>[0-9a-zA-Z_.]*)/(?P<form_id>[a-zA-Z_-]*)/(?P<resourceid>%s|())$' % uuid_regex, 'arches.app.views.resources.resource_manager', name="resource_manager"),
    url(r'^resources/related/(?P<resourceid>%s|())$' % uuid_regex, 'arches.app.views.resources.related_resources', name="related_resources"),
    url(r'^resources/history/(?P<resourceid>%s|())$' % uuid_regex, 'arches.app.views.resources.edit_history', name="edit_history"),
    url(r'^resources/layers/(?P<entitytypeid>.*)$', 'arches.app.views.resources.map_layers', name="map_layers"),
    url(r'^resources/markers/(?P<entitytypeid>.*)$', 'arches.app.views.resources.map_layers', {'get_centroids':True}, name="map_markers"),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()
