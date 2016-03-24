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

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.utils.translation import ugettext as _
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.models.resource_graphs import ResourceGraph

@csrf_exempt
def manager(request, nodeid):
    graph = ResourceGraph({"nodes": [], "edges": []})
    graph.get_graph_from_rootid(nodeid)
    return render(request, 'graph-manager.htm', {
        'main_script': 'graph-manager',
        'graph': JSONSerializer().serialize(graph),
        'node_list': {
            'title': _('Node List'),
            'search_placeholder': _('Find a node in the graph')
        }
    })
