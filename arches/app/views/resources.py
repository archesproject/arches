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
from django.db import transaction
from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.models.concept import Concept
from django.utils.translation import ugettext as _
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

@csrf_exempt
def resource_manager(request, resourcetypeid=None, form_id=None, resourceid=None):

    if resourceid != None:
        resource = Resource(resourceid)
    elif resourcetypeid != None:
        resource = Resource({'entitytypeid': resourcetypeid})

    form = resource.get_form(form_id)

    if request.method == 'POST':
        # get the values from the form and pass to the resource
        data = JSONDeserializer().deserialize(request.POST.get('formdata', {}))
        form.update(data)

        with transaction.atomic():
            resource.save()
            resource.index()
            resourceid = resource.entityid

            return redirect('resource_manager', resourcetypeid=resourcetypeid, form_id=form_id, resourceid=resourceid)

    return render_to_response('resource-manager.htm', {
            'form': form,
            'formdata': JSONSerializer().serialize(form.data),
            'form_template': 'forms/' + form_id + '.htm',
            'form_id': form_id,
            'resourcetypeid': resourcetypeid,
            'main_script': 'resource-manager',
            'active_page': 'ResourceManger',
            'resource': resource,
            'resource_name': resource.get_primary_name(),
            'resource_type_name': resource.get_type_name(),
            'form_groups': resource.form_groups
        },
        context_instance=RequestContext(request))        



class ResourceForm(object):
    id = ''
    icon = ''
    name = ''

    def __init__(self, resource):
        # here is where we can create the basic format for the form data
        self.resource = resource
        self.data = {
            "domains": {},
            "defaults": {}
        }
        self.load()

	def update(self, data):
		# update resource w/ post data
		return 

    def get_e55_domain(self, entitytypeid):
        return list(models.VwEntitytypeDomains.objects.filter(entitytypeid=entitytypeid).order_by('sortorder', 'value').values())

    def get_nodes(self, entitytypeid):
        ret = []
        entities = self.resource.find_entities_by_type_id(entitytypeid)
        for entity in entities:
            data = {}

            for entity in entity.flatten():
                #data[entity.entitytypeid] = self.encode_entity(entity)
                data = dict(data.items() + self.encode_entity(entity).items())
            ret.append(data)
        return ret

    def encode_entity(self, entity):
        def enc(entity, attr):
            return '%s__%s' % (entity.entitytypeid.replace('.', '_'), attr)

        ret = {}
        for key, value in entity.__dict__.items():
            if not key.startswith("__"):
                ret[enc(entity, key)] = value
        return ret

    def decode_data_item(self, entity):
        def dec(item):
            # item = "NAME_E41__entitytypeid"
            val = item.split('__')
            if len(val) != 2:
                return False
            entitytypeid = val[0]
            propertyname = val[1]
            
            v = entitytypeid.split('_')
            entitytypeid = '%s.%s' % ('_'.join(v[:-1]), v[-1])
            return (entitytypeid, propertyname)

        ret = {}
        for key, value in entity.iteritems():
            r = dec(key)
            if r:
                if r[0] not in ret:
                    ret[r[0]] = {}
                ret[r[0]][r[1]] = value

        ret2 = []
        for key, value in ret.iteritems():
            value['entitytypeid'] = key
            ret2.append(value)
        return ret2