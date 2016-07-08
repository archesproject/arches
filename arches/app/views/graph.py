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

from django.conf import settings as app_settings
from django.db import transaction
from django.shortcuts import render
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.http import HttpResponseNotFound, QueryDict
from arches.app.utils.decorators import group_required
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.JSONResponse import JSONResponse
from arches.app.models.graph import Graph
from arches.app.models import models

def test(request, graphid):
    #graph = Graph.objects.filter(isresource=True)
    # node = models.Node.objects.get(pk='7f5ada4c-3e29-11e6-a8d1-14109fd34195')
    # graph = Graph.objects.get(node=node)
    graph = Graph.objects.get(graphid=graphid)
    return JSONResponse(graph, indent=4)

@group_required('edit')
def manager(request, graphid):
    if request.method == 'DELETE':
        graph = Graph.objects.get(pk=graphid)
        graph.delete()
        return JSONResponse({'succces':True})

    graphs = models.GraphModel.objects.all()
    if graphid is None or graphid == '':
        return render(request, 'views/graph/graph-list.htm', {
            'main_script': 'views/graph/graph-list',
            'graphs': JSONSerializer().serialize(graphs)
        })

    graph = Graph.objects.get(graphid=graphid)
    validations = models.Validation.objects.all()
    branch_graphs = Graph.objects.exclude(pk=graphid)
    if graph.ontology is not None:
        branch_graphs = branch_graphs.filter(ontology=graph.ontology)
    datatypes = models.DDataType.objects.all()
    return render(request, 'views/graph/graph-manager.htm', {
        'main_script': 'views/graph/graph-manager',
        'graphid': graphid,
        'graphs': JSONSerializer().serialize(graphs),
        'graph': JSONSerializer().serializeToPython(graph),
        'graph_json': JSONSerializer().serialize(graph),
        'validations': JSONSerializer().serialize(validations),
        'branches': JSONSerializer().serialize(branch_graphs),
        'datatypes': JSONSerializer().serialize(datatypes),
        'node_list': {
            'title': _('Node List'),
            'search_placeholder': _('Find a node...')
        },
        'permissions_list': {
            'title': _('Permissions'),
            'search_placeholder': _('Find a group or user account')
        },
        'branch_list': {
            'title': _('Branch Library'),
            'search_placeholder': _('Find a graph branch')
        }
    })


@group_required('edit')
def settings(request, graphid):
    node = models.Node.objects.get(graph_id=graphid, istopnode=True)
    graph = node.graph
    if request.method == 'POST':
        data = JSONDeserializer().deserialize(request.body)
        for key, value in data.get('graph').iteritems():
            setattr(graph, key, value)
        graph.save()
        node.set_relatable_resources(data.get('relatable_resource_ids'))
        node.ontologyclass = data.get('ontology_class') if graph.ontology is not None else None
        node.save()
        return JSONResponse({
            'success': True,
            'graph': graph,
            'relatable_resource_ids': [res.nodeid for res in node.get_relatable_resources()]
        })
    node_json = JSONSerializer().serialize(node)
    icons = models.Icon.objects.order_by('name')
    resource_graphs = models.GraphModel.objects.filter(Q(isresource=True), ~Q(graphid=graphid))
    resource_data = []
    relatable_resources = node.get_relatable_resources()
    for res in resource_graphs:
        if models.Node.objects.filter(graph=res, istopnode=True).count() > 0:
            node = models.Node.objects.get(graph=res, istopnode=True)
            resource_data.append({
                'id': node.nodeid,
                'graph': res,
                'is_relatable': (node in relatable_resources)
            })
    graphs = models.GraphModel.objects.all()
    ontologies = models.Ontology.objects.filter(parentontology=None)
    ontology_classes = models.OntologyClass.objects.values('source', 'ontology_id')
    return render(request, 'views/graph/graph-settings.htm', {
        'main_script': 'views/graph/graph-settings',
        'icons': JSONSerializer().serialize(icons),
        'graph': JSONSerializer().serialize(graph),
        'node_json': node_json,
        'graphs': JSONSerializer().serialize(graphs),
        'ontologies': JSONSerializer().serialize(ontologies),
        'ontology_classes': JSONSerializer().serialize(ontology_classes),
        'graphid': graphid,
        'resource_data': JSONSerializer().serialize(resource_data),
        'node_count': models.Node.objects.filter(graph=graph).count()
    })

@group_required('edit')
def card_manager(request, graphid):
    graph = Graph.objects.get(graphid=graphid)
    graph.include_cards = True
    
    graphs = models.GraphModel.objects.all()
    branch_graphs = graphs.exclude(pk=graphid)
    if graph.ontology is not None:
        branch_graphs = branch_graphs.filter(ontology=graph.ontology)
    
    branches = JSONSerializer().serializeToPython(branch_graphs)
    for branch in branches:
        branch_graph = Graph(branch['graphid'])
        branch_graph.include_cards = True
        branch['graph'] = branch_graph

    return render(request, 'views/graph/card-manager.htm', {
        'main_script': 'views/graph/card-manager',
        'graphid': graphid,
        'graph': JSONSerializer().serialize(graph),
        'graphs': JSONSerializer().serialize(branches)
    })

@group_required('edit')
def node(request, graphid):
    data = JSONDeserializer().deserialize(request.body)
    if data:
        if request.method == 'POST':
            graph = Graph.objects.get(graphid=graphid)
            graph.update_node(data)
            graph.save()
            return JSONResponse(graph)

    return HttpResponseNotFound()

@group_required('edit')
def delete_node(request, graphid):
    data = JSONDeserializer().deserialize(request.body)
    if data:
        if request.method == 'DELETE':
            graph = Graph.objects.get(graphid=graphid)
            graph.delete_node(node=data.get('nodeid', None))
            return JSONResponse({})

    return HttpResponseNotFound()

@group_required('edit')
def append_branch(request, graphid):
    if request.method == 'POST':
        data = JSONDeserializer().deserialize(request.body)
        graph = Graph.objects.get(graphid=graphid)
        new_branch = graph.append_branch(data['property'], nodeid=data['nodeid'], graphid=data['graphid'])
        graph.save()
        return JSONResponse(new_branch)

    return HttpResponseNotFound()

@group_required('edit')
def move_node(request, graphid):
    if request.method == 'POST':
        data = JSONDeserializer().deserialize(request.body)
        graph = Graph.objects.get(graphid=graphid)
        updated_nodes_and_edges = graph.move_node(data['nodeid'], data['property'], data['newparentnodeid'])
        graph.save()
        return JSONResponse(updated_nodes_and_edges)

    return HttpResponseNotFound()

@group_required('edit')
def clone(request, graphid):
    if request.method == 'POST':
        data = JSONDeserializer().deserialize(request.body)
        graph = Graph.objects.get(graphid=graphid).copy()
        if 'isresource' in data:
            graph.isresource = data['isresource']

        if 'name' in data:
            name = data['name']
        else:
            name = _('New Resource') if graph.isresource else _('New Graph')
        graph.root.name = name
        graph.name = name

        graph.save()
        return JSONResponse(graph)

    return HttpResponseNotFound()

@group_required('edit')
def new(request):
    if request.method == 'POST':
        data = JSONDeserializer().deserialize(request.body)
        isresource = data['isresource'] if 'isresource' in data else False
        name = _('New Resource') if isresource else _('New Graph')
        author = request.user.first_name + ' ' + request.user.last_name
        graph = Graph.new(name=name,is_resource=isresource,author=author)
        graph.save()
        return JSONResponse(graph)

    return HttpResponseNotFound()

def get_related_nodes(request, graphid):
    data = JSONDeserializer().deserialize(request.body)
    graph = Graph.objects.get(graphid=graphid)
    return JSONResponse(graph.get_valid_ontology_classes(nodeid=data['nodeid']))

def get_valid_domain_nodes(request, graphid):
    data = JSONDeserializer().deserialize(request.body)
    graph = Graph.objects.get(graphid=graphid)
    return JSONResponse(graph.get_valid_domain_ontology_classes(nodeid=data['nodeid']))
