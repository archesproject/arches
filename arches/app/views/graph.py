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


@group_required('edit')
def manager(request, nodeid):
    if nodeid is None or nodeid == '':
        graphs = models.Node.objects.filter(istopnode=True)
        metadata = models.GraphMetadata.objects.all()
        return render(request, 'graph-list.htm', {
            'main_script': 'graph-list',
            'graphs': JSONSerializer().serialize(graphs),
            'metadata': JSONSerializer().serialize(metadata)
        })

    graph = Graph(nodeid)
    validations = models.Validation.objects.all()
    metadata_records = JSONSerializer().serializeToPython(models.GraphMetadata.objects.all())
    branch_nodes = models.Node.objects.filter(~Q(graphmetadata=None), istopnode=True)

    branches = []
    for metadata_record in metadata_records:
        try:
            rootnode = branch_nodes.get(graphmetadata_id=metadata_record['graphmetadataid'])
            metadata_record['graph'] = Graph(rootnode)
            metadata_record['relates_via'] = ['P1', 'P2', 'P3']
            branches.append(metadata_record)
        except models.Node.DoesNotExist:
            pass

    datatypes = models.DDataType.objects.all()
    return render(request, 'graph-manager.htm', {
        'main_script': 'graph-manager',
        'nodeid': nodeid,
        'graph': JSONSerializer().serialize(graph),
        'validations': JSONSerializer().serialize(validations),
        'branches': JSONSerializer().serialize(branches),
        'datatypes': JSONSerializer().serialize(datatypes),
        'node_list': {
            'title': _('Node List'),
            'search_placeholder': _('Find a node in the graph')
        },
        'permissions_list': {
            'title': _('Permissions'),
            'search_placeholder': _('Find a group or user account')
        },
        'branch_list': {
            'title': _('Branch Library'),
            'search_placeholder': _('Find a graph branch')
        },
        'metadata': graph.root.graphmetadata
    })


@group_required('edit')
def settings(request, nodeid):
    node = models.Node.objects.get(nodeid=nodeid)
    if request.method == 'POST':
        data = JSONDeserializer().deserialize(request.body)
        for key, value in data.iteritems():
            setattr(node.graphmetadata, key, value)
        node.graphmetadata.save()
        return JSONResponse({'success': True, 'metadata': node.graphmetadata})
    icons = models.Icon.objects.order_by('name')
    return render(request, 'graph-settings.htm', {
        'main_script': 'graph-settings',
        'icons': JSONSerializer().serialize(icons),
        'node': JSONSerializer().serialize(node),
        'metadata_json': JSONSerializer().serialize(node.graphmetadata),
        'nodeid': nodeid,
        'metadata': node.graphmetadata
    })


@group_required('edit')
def node(request, nodeid):
    if request.method == 'POST':
        data = JSONDeserializer().deserialize(request.body)
        if data:
            node = models.Node.objects.get(nodeid=nodeid)
            nodes, edges = node.get_child_nodes_and_edges()
            collectors = [node_ for node_ in nodes if node_.is_collector()]
            node_ids = [id_node.nodeid for id_node in nodes]
            nodes = [node_ for node_ in nodes if (node_.nodegroup_id not in node_ids)]
            with transaction.atomic():
                node.name = data.get('name', '')
                node.description = data.get('description', '')
                node.istopnode = data.get('istopnode', '')
                node.crmclass = data.get('crmclass', '')
                node.datatype = data.get('datatype', '')
                node.status = data.get('status', '')
                node.validations.set(data.get('validations', []))
                new_nodegroup_id = data.get('nodegroup_id', None)
                cardinality = data.get('cardinality', 'n')
                if unicode(node.nodegroup_id) != new_nodegroup_id:
                    edge = models.Edge.objects.get(rangenode_id=nodeid)
                    parent_group = edge.domainnode.nodegroup
                    new_group = parent_group
                    if new_nodegroup_id == nodeid:
                        new_group, created = models.NodeGroup.objects.get_or_create(nodegroupid=nodeid, defaults={'cardinality': 'n', 'legacygroupid': None, 'parentnodegroup': None})
                        new_group.parentnodegroup = parent_group
                        new_group.cardinality = cardinality
                        new_group.save()
                        parent_group = new_group

                    for collector in collectors:
                        collector.nodegroup.parentnodegroup = parent_group
                        collector.nodegroup.save()

                    for group_node in nodes:
                        group_node.nodegroup = new_group
                        group_node.save()

                    node.nodegroup = new_group

                node.save()
                return JSONResponse({'node': node, 'group_nodes': nodes, 'collectors': collectors, 'nodegroup': node.nodegroup})

    if request.method == 'DELETE':
        node = models.Node.objects.get(nodeid=nodeid)
        nodes, edges = node.get_child_nodes_and_edges()
        if not node.istopnode:
            edges.append(models.Edge.objects.get(rangenode=node))
        nodes.append(node)
        with transaction.atomic():
            [edge.delete() for edge in edges]
            [node.delete() for node in nodes]
            return JSONResponse({})

    return HttpResponseNotFound()

@group_required('edit')
def append_branch(request, nodeid, property, graphmetadataid):
    if request.method == 'POST':
        graph = Graph(nodeid)
        newBranch = graph.append_branch(property, graphmetadataid=graphmetadataid)
        graph.save()
        return JSONResponse(newBranch)

    return HttpResponseNotFound()

@group_required('edit')
def move_node(request, nodeid):
    if request.method == 'POST':
        data = JSONDeserializer().deserialize(request.body)
        graph = Graph(nodeid)
        updated_nodes_and_edges = graph.move_node(data['nodeid'], data['property'], data['newparentnodeid'])
        graph.save()
        return JSONResponse(updated_nodes_and_edges)

    return HttpResponseNotFound()

@group_required('edit')
def clone(request, nodeid):
    if request.method == 'POST':
        data = JSONDeserializer().deserialize(request.body)
        graph = Graph(nodeid).copy()
        if 'name' in data:
            graph.root.name = data['name']
        graph.root.graphmetadata = None
        graph.populate_null_nodegroups()
        graph.save()
        return JSONResponse(graph)

    return HttpResponseNotFound()
