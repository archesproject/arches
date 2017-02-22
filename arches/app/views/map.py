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
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from arches.app.models import models
from arches.app.views.base import BaseManagerView
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.utils.decorators import group_required


@method_decorator(group_required('edit'), name='dispatch')
class MapLayerManagerView(BaseManagerView):
    def get(self, request):
        datatype_factory = DataTypeFactory()
        datatypes = models.DDataType.objects.all()
        widgets = models.Widget.objects.all()
        map_layers = models.MapLayers.objects.all()
        map_sources = models.MapSources.objects.all()
        context = self.get_context_data(
            datatypes=datatypes,
            widgets=widgets,
            map_layers=map_layers,
            map_sources=map_sources,
            datatypes_json=JSONSerializer().serialize(datatypes),
            main_script='views/map-layer-manager',
        )

        context['geom_nodes_json'] = JSONSerializer().serialize(context['geom_nodes'])
        resource_layers = []
        resource_sources = []
        for node in context['geom_nodes']:
            datatype = datatype_factory.get_instance(node.datatype)
            map_layer = datatype.get_map_layer(node=node, preview=True)
            if map_layer is not None:
                resource_layers.append(map_layer)
            map_source = datatype.get_map_source(node=node, preview=True)
            if map_source is not None:
                resource_sources.append(map_source)
        context['resource_map_layers_json'] = JSONSerializer().serialize(resource_layers)
        context['resource_map_sources_json'] = JSONSerializer().serialize(resource_sources)

        context['nav']['title'] = _('Map Layer Manager')
        context['nav']['icon'] = 'fa-server'
        context['nav']['help'] = (_('Map Layer Manager'),'')

        return render(request, 'views/map-layer-manager.htm', context)
