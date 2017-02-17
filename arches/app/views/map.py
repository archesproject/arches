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
from django.shortcuts import render
from django.utils.translation import ugettext as _
from arches.app.models import models
from arches.app.views.base import BaseManagerView


class MapLayerManagerView(BaseManagerView):
    def get(self, request):
        map_layers = models.MapLayers.objects.all()
        map_sources = models.MapSources.objects.all()
        date_nodes = models.Node.objects.filter(datatype='date', graph__isresource=True, graph__isactive=True)

        context = self.get_context_data(
            date_nodes=date_nodes,
            map_layers=map_layers,
            map_sources=map_sources,
            main_script='views/map-layer-manager',
        )

        context['nav']['title'] = _('Map Layer Manager')
        context['nav']['icon'] = 'fa-server'
        context['nav']['help'] = (_('Map Layer Manager'),'')

        return render(request, 'views/map-layer-manager.htm', context)
