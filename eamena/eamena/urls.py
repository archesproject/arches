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

from arches import urls as arches_urls
from django.conf.urls import patterns, url, include

uuid_regex = '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'

urlpatterns = patterns('',
    url(r'^search$', 'eamena.views.search.home_page', name="search_home"),
    url(r'^bulk-upload/$', 'eamena.views.bulk_upload.main', name="bulk_upload"),
    url(r'^bulk-upload/new$', 'eamena.views.bulk_upload.new_upload', name="new_upload"),
    url(r'^bulk-upload/excel-upload$', 'eamena.views.bulk_upload.upload_spreadsheet', name="excel_upload"),
    url(r'^bulk-upload/validate$', 'eamena.views.bulk_upload.validate', name="excel_validate"),
    url(r'^bulk-upload/import$', 'eamena.views.bulk_upload.import_archesfile', name="excel_import"),
    url(r'^bulk-upload/attachments$', 'eamena.views.bulk_upload.upload_attachments', name='upload_attachments'),
    url(r'^search/resources$', 'eamena.views.search.search_results', name="search_results"),
    url(r'^search/export$', 'eamena.views.search.export_results', name="search_results_export"),
    url(r'^reports/(?P<resourceid>%s)$' % uuid_regex , 'eamena.views.resources.report', name='report'),
    url('^', include('django.contrib.auth.urls')),
    url(r'^admin/auth/user/(?P<userid>[0-9]*)/user_activity/$' , 'eamena.views.user_activity.user_activity', name='user_activity'),
    url(r'^admin/auth/group/(?P<groupid>[0-9]*)/group_activity/$' , 'eamena.views.group_activity.group_activity', name='group_activity'),
    url(r'^admin/auth/user/(?P<userid>[0-9]*)/user_activity_data/$' , 'eamena.views.user_activity.user_activity_data', name='user_activity_data'),
    url(r'^admin/auth/group/(?P<groupid>[0-9]*)/group_activity_data/$' , 'eamena.views.group_activity.group_activity_data', name='group_activity_data'),
    url(r'^search/overlaps', 'eamena.views.search.find_overlapping', name="find_overlapping_data"),
    url(r'', include(arches_urls)),
)

