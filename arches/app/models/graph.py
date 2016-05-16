
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

import uuid
from copy import copy
from django.db import transaction
from arches.app.models import models
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer


class Graph(object):
    """
    Used for mapping complete resource graph objects to and from the database

    """

    def __init__(self, *args, **kwargs):
        self.root = None
        self.nodes = {}
        self.edges = {}
        self.nodegroups = {}
        self.metadata = {}

        if args:
            if isinstance(args[0], dict):
                self.metadata = models.Graph()
                for node in args[0]["nodes"]:
                    newNode = self.add_node(node)
                    if node['istopnode']:
                        self.root = newNode

                for edge in args[0]["edges"]:
                    self.add_edge(edge)

                self.populate_null_nodegroups()

                metadata_dict = args[0]["metadata"]
                for key, value in metadata_dict.iteritems():
                    setattr(self.metadata, key, value)
            else:
                if (isinstance(args[0], basestring) or
                   isinstance(args[0], uuid.UUID)):
                    self.metadata = models.Graph.objects.get(pk=args[0])
                elif isinstance(args[0], models.Graph):
                    self.metadata = args[0]
                elif isinstance(args[0], models.Node):
                    self.metadata = args[0].graph
                self.root = self.metadata.node_set.get(istopnode=True)
                nodes = self.metadata.node_set.all()
                edges = self.metadata.edge_set.all()
                for node in nodes:
                    self.add_node(node)
                for edge in edges:
                    edge.domainnode = self.nodes[edge.domainnode.pk]
                    edge.rangenode = self.nodes[edge.rangenode.pk]
                    self.add_edge(edge)


    def add_node(self, node):
        """
        Adds a node to this graph

        Arguments:
        node -- a dictionary representing a Node instance or an actual models.Node instance

        """
        if not isinstance(node, models.Node):
            nodeobj = node.copy()
            node = models.Node()
            node.nodeid = nodeobj.get('nodeid', None)
            node.name = nodeobj.get('name', '')
            node.description = nodeobj.get('description','')
            node.istopnode = nodeobj.get('istopnode','')
            node.ontologyclass_id = nodeobj.get('ontologyclass','')
            node.datatype = nodeobj.get('datatype','')
            node.nodegroup_id = nodeobj.get('nodegroupid','')

            if node.nodegroup_id != None and node.nodegroup_id != '':
                node.nodegroup = models.NodeGroup(
                    pk=node.nodegroup_id,
                    cardinality=nodeobj.get('cardinality', '')
                )

        node.graph = self.metadata

        if node.pk == None:
            node.pk = uuid.uuid1()
        if node.nodegroup != None:
            self.nodegroups[node.nodegroup.pk] = node.nodegroup
        self.nodes[node.pk] = node
        return node

    def add_edge(self, edge):
        """
        Adds an edge to this graph

        will throw an error if the domain or range nodes referenced in this edge haven't
        already been added to this graph

        Arguments:
        edge -- a dictionary representing a Edge instance or an actual models.Edge instance

        """
        if not isinstance(edge, models.Edge):
            egdeobj = edge.copy()
            edge = models.Edge()
            edge.edgeid = egdeobj.get('edgeid', None)
            edge.rangenode = self.nodes[egdeobj.get('rangenodeid')]
            edge.domainnode = self.nodes[egdeobj.get('domainnodeid')]
            edge.ontologyproperty_id = egdeobj.get('ontologyproperty', '')

        edge.graph = self.metadata

        if edge.pk == None:
            edge.pk = uuid.uuid1()
        self.edges[edge.pk] = edge
        return edge

    def save(self):
        """
        Saves an entity back to the db, returns a DB model instance, not an instance of self

        """

        with transaction.atomic():
            self.metadata.save()

            for nodegroup_id, nodegroup in self.nodegroups.iteritems():
                nodegroup.save()

            for node_id, node in self.nodes.iteritems():
                node.save()

            for edge_id, edge in self.edges.iteritems():
                edge.save()


    def get_tree(self, root=None):
        """
        returns a tree based representation of this graph

        Keyword Arguments:
        root -- the node from which to root the tree, defaults to the root node of this graph

        """

        tree = {
            'node': root if root else self.root,
            'children': []
        }

        def find_child_edges(tree):
            for edge_id, edge in self.edges.iteritems():
                if edge.domainnode == tree['node']:
                    tree['children'].append(find_child_edges({
                        'node': edge.rangenode,
                        'children':[]
                    }))

            return tree

        return find_child_edges(tree)

    def populate_null_nodegroups(self):
        """
        populates any blank nodegroup ids of the nodes in this graph with the nearest parent node

        """

        tree = self.get_tree()

        def traverse_tree(tree, current_nodegroup=None):
            if tree['node'].nodegroup == None:
                tree['node'].nodegroup = current_nodegroup
            else:
                current_nodegroup = models.NodeGroup(
                    pk=tree['node'].nodegroup_id,
                    parentnodegroup=current_nodegroup
                )

            for child in tree['children']:
                traverse_tree(child, current_nodegroup)
            return tree

        return traverse_tree(tree)

    def append_branch(self, property, nodeid=None, graphid=None):
        """
        Appends a branch onto this graph

        Arguments:
        property -- the property to use when appending the branch

        Keyword Arguments:
        nodeid -- if given will append the branch to this node, if not supplied will
        append the branch to the root of this graph

        graphid -- get the branch to append based on the graphid
        """
        branch_graph = Graph(graphid)

        branch_copy = branch_graph.copy()
        branch_copy.root.istopnode = False

        with transaction.atomic():
            newEdge = models.Edge(
                domainnode = (self.nodes[uuid.UUID(nodeid)] if nodeid else self.root),
                rangenode = branch_copy.root,
                ontologyproperty_id = property,
                graph = self.metadata
            )
            branch_copy.add_edge(newEdge)
        for key, node in branch_copy.nodes.iteritems():
            self.add_node(node)
        for key, edge in branch_copy.edges.iteritems():
            self.add_edge(edge)

        self.populate_null_nodegroups()
        return branch_copy

    def copy(self):
        """
        returns an unsaved copy of self

        """

        new_nodegroups = {}

        copy_of_self = Graph(self.metadata.pk)
        node_ids = sorted(copy_of_self.nodes, key=lambda node_id: copy_of_self.nodes[node_id].is_collector(), reverse=True)

        copy_of_self.metadata.pk = uuid.uuid1()
        for node_id in node_ids:
            node = copy_of_self.nodes[node_id]
            if node == self.root:
                copy_of_self.root = node
            node.graph = copy_of_self.metadata
            is_collector = node.is_collector()
            node.pk = uuid.uuid1()
            if is_collector:
                new_nodegroups[node.nodegroup.pk] = node.nodegroup
                node.nodegroup_id = node.nodegroup.pk = node.pk
            elif node.nodegroup and node.nodegroup.pk in new_nodegroups:
                node.nodegroup_id = new_nodegroups[node.nodegroup.pk].pk
                node.nodegroup = new_nodegroups[node.nodegroup.pk]

        copy_of_self.nodes = {node.pk:node for node_id, node in copy_of_self.nodes.iteritems()}

        for edge_id, edge in copy_of_self.edges.iteritems():
            edge.pk = uuid.uuid1()
            edge.graph = copy_of_self.metadata
            edge.domainnode_id = edge.domainnode.pk
            edge.rangenode_id = edge.rangenode.pk

        copy_of_self.edges = {edge.pk:edge for edge_id, edge in copy_of_self.edges.iteritems()}

        copy_of_self.nodegroups = new_nodegroups

        return copy_of_self

    def move_node(self, nodeid, property, newparentnodeid):
        """
        move a node and it's children to a different location within this graph

        Arguments:
        nodeid -- the id of node being moved

        property -- the property value to conect the node to it's new parent nodegroup

        newparentnodeid -- the parent node id that the node is being moved to

        """

        ret = {'nodes':[], 'edges':[]}
        nodegroup = None
        node = self.nodes[uuid.UUID(str(nodeid))]
        if not node.is_collector():
            nodegroup = node.nodegroup

            child_nodes, child_edges = node.get_child_nodes_and_edges()
            child_nodes.append(node)
            for child_node in child_nodes:
                if child_node.nodegroup == nodegroup:
                    self.nodes[child_node.pk].nodegroup = None
                    ret['nodes'].append(child_node)

        for edge_id, edge in self.edges.iteritems():
            if edge.rangenode == node:
                edge.domainnode = self.nodes[uuid.UUID(str(newparentnodeid))]
                ret['edges'].append(edge)

        self.populate_null_nodegroups()
        return ret

    def serialize(self):
        ret = {}
        ret['metadata'] = self.metadata
        ret['root'] = self.root
        ret['nodegroups'] = [nodegroup for key, nodegroup in self.nodegroups.iteritems()]
        ret['nodes'] = [node for key, node in self.nodes.iteritems()]
        ret['edges'] = [edge for key, edge in self.edges.iteritems()]
        return ret
