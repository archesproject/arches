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

from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.conf import settings
from arches.app.models.resource import Resource
from django.utils.translation import ugettext as _

def resource_manager(request, resourcetypeid=None, form_id=None, resourceid=None):
    resource = Resource()

    return render_to_response('resource-manager.htm', {
            'form_template': 'forms/' + form_id + '.htm',
            'form_id': form_id,
            'main_script': 'resource-manager',
            'active_page': 'ResourceManger',
            'resource': resource,
            'resource_name': resource.get_name(),
            'resource_type_name': resource.get_type_name(),
            'form_groups': resource.get_forms()        
        },
        context_instance=RequestContext(request))


class ResourceForm(object):
	id = ''
	icon = ''
	name = ''

	def __init__(self, resource=None):
		# here is where we can create the basic format for the form data
		self.resource = resource
		self.data = {}

	def update(self, post_data):
		# update resource w/ post data
		return self.resource


# class TestForm(ResourceForm):
# 	id = 'test-form'
# 	icon = 'fa-folder'
# 	name = _('Test Form')


# # mocked up for form collection
# class FakeResource():
# 	id = None
# 	form_groups = [{
# 		'id': 'resource-description',
# 		'icon':'fa-folder',
# 		'name': _('Resource Description'),
# 		'forms': [
# 			TestForm()
# 		]
# 	},{
# 		'id': 'resource-evaluation',
# 		'icon': 'fa-dashboard',
# 		'name': _('Evaluate Resource'),
# 		'forms': []
# 	}]

# 	def get_forms(self, form_id=None):
# 		if form_id:
# 			selected_form = None
# 			forms = [form for group in self.form_groups for form in group.forms]
# 			for form in forms:
# 				if form.id == form_id:
# 					selected_form = form
# 			return selected_form
# 		else:
# 			return self.form_groups

# 	def get_type_name(self):
# 		return _('Test Resource')

# 	def get_name(self):
# 		return _('Unnamed Resource')


# def new(request, entitytypeid):
# 	resource = FakeResource()
# 	return render_to_response('resource-manager.htm', {
#             'main_script': 'resource-manager',
#             'active_page': 'Home',
#             'resource': resource,
#             'resource_name': resource.get_name(),
#             'resource_type_name': resource.get_type_name(),
#             'form_groups': resource.get_forms()
#         },
#         context_instance=RequestContext(request))
