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


from arches.app.models import models
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from django.views.generic import TemplateView
from arches.app.datatypes.datatypes import DataTypeFactory

class BaseManagerView(TemplateView):

    template_name = ''

    def get_context_data(self, **kwargs):
        datatype_factory = DataTypeFactory()
        context = super(BaseManagerView, self).get_context_data(**kwargs)
        context['graph_models'] = models.GraphModel.objects.all()
        context['graphs'] = JSONSerializer().serialize(context['graph_models'])
        context['nav'] = {
            'icon':'fa fa-chevron-circle-right',
            'title':'',
            'help':('',''),
            'menu':False,
            'search':True,
            'res_edit':False,
            'edit_history':False,
            'login':True,
            'print':False,
        }
        geom_datatypes = [d.pk for d in models.DDataType.objects.filter(isgeometric=True)]
        geom_nodes = models.Node.objects.filter(graph__isresource=True, datatype__in=geom_datatypes)
        resource_layers = []
        resource_sources = []
        for node in geom_nodes:
            datatype = datatype_factory.get_instance(node.datatype)
            map_source = datatype.get_map_source(node)
            if map_source is not None:
                resource_sources.append(map_source)
            map_layer = datatype.get_map_layer(node)
            if map_layer is not None:
                resource_layers.append(map_layer)

        context['resource_map_layers'] = resource_layers
        context['resource_map_sources'] = resource_sources

        return context
