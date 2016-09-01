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

import itertools
from django.conf import settings as app_settings
from django.db import transaction
from django.shortcuts import render
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.http import HttpResponseNotFound, QueryDict, HttpResponse
from arches.app.utils.decorators import group_required
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.JSONResponse import JSONResponse
from arches.app.models.graph import Graph
from arches.app.models.card import Card
from arches.app.models import models
from arches.app.utils.data_management.resource_graphs.exporter import get_graphs_for_export
from tempfile import NamedTemporaryFile
from guardian.shortcuts import get_perms_for_model
import json


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
    branch_graphs = Graph.objects.exclude(pk=graphid).exclude(isresource=True).exclude(isactive=False)
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
        'datatypes_json': JSONSerializer().serialize(datatypes),
        'datatypes': datatypes,
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
        'graph_json': JSONSerializer().serialize(graph),
        'graph': JSONSerializer().serializeToPython(graph),
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
    branch_graphs = Graph.objects.exclude(pk=graphid).exclude(isresource=True).exclude(isactive=False)
    if graph.ontology is not None:
        branch_graphs = branch_graphs.filter(ontology=graph.ontology)

    return render(request, 'views/graph/card-manager.htm', {
        'main_script': 'views/graph/card-manager',
        'graphid': graphid,
        'graph': JSONSerializer().serializeToPython(graph),
        'graphJSON': JSONSerializer().serialize(graph),
        'graphs': JSONSerializer().serialize(models.GraphModel.objects.all()),
        'branches': JSONSerializer().serialize(branch_graphs)
    })
    graph = Graph.objects.get(graphid=graphid)
    validations = models.Validation.objects.all()

@group_required('edit')
def card(request, cardid):
    if request.method == 'POST':
        data = JSONDeserializer().deserialize(request.body)
        if data:
            card = Card(data)
            card.save()
            return JSONResponse(card)

    if request.method == 'GET':
        try:
            card = Card.objects.get(cardid=cardid)
        except(Card.DoesNotExist):
            # assume this is a graph id
            card = Card.objects.get(cardid=Graph.objects.get(graphid=cardid).get_root_card().cardid)
        datatypes = models.DDataType.objects.all()
        widgets = models.Widget.objects.all()
        validations = models.Validation.objects.all()
        graph = Graph.objects.get(graphid=card.graph_id)
        return render(request, 'views/graph/card-configuration-manager.htm', {
            'main_script': 'views/graph/card-configuration-manager',
            'graphid': card.graph_id,
            'graph': JSONSerializer().serializeToPython(graph),
            'graphs': JSONSerializer().serialize(models.GraphModel.objects.all()),
            'card': JSONSerializer().serialize(card),
            'permissions': JSONSerializer().serialize([{'codename': permission.codename, 'name': permission.name} for permission in get_perms_for_model(card.nodegroup)]),
            'datatypes_json': JSONSerializer().serialize(datatypes),
            'datatypes': datatypes,
            'widgets': widgets,
            'widgets_json': JSONSerializer().serialize(widgets),
            'validations': JSONSerializer().serialize(validations),
        })

    return HttpResponseNotFound()

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
        graph.save()
        return JSONResponse(graph)

    return HttpResponseNotFound()

@group_required('edit')
def export_graph(request, graphid):
    if request.method == 'GET':
        graph = get_graphs_for_export([graphid])
        f = JSONSerializer().serialize(graph)
        graph_name = JSONDeserializer().deserialize(f)['graph'][0]['name']

        response = HttpResponse(f, content_type='json/plain')
        response['Content-Disposition'] = 'attachment; filename="%s export.json"' %(graph_name)
        return response

    return HttpResponseNotFound()

@group_required('edit')
def import_graph(request):
    if request.method == 'POST':
        graph_file = request.FILES.get('importedGraph').read()
        graphs = JSONDeserializer().deserialize(graph_file)['graph']
        for graph in graphs:
            new_graph = Graph(graph)
            new_graph.save()

        return JSONResponse({})

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

def datatype_template(request, template="text"):
    return render(request, 'views/graph/datatypes/%s.htm' % template)
