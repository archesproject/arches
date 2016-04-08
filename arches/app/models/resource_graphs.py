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

class ResourceGraph(object):
    """
    Used for mapping complete resource graph objects to and from the database

    """

    def __init__(self, *args, **kwargs):
        self.root = None
        self.nodes = {}
        self.edges = {}
        if args:
            if (isinstance(args[0], basestring) or
               isinstance(args[0], uuid.UUID)):
                root = models.Node.objects.get(pk=args[0])
                self.get_nodes_and_edges(root)
            elif isinstance(args[0], models.Node):
                self.get_nodes_and_edges(args[0])
            elif args[0]["nodes"] and args[0]["edges"]:
                for node in args[0]["nodes"]:
                    newNode = self.addNode(node)
                    if node['istopnode']:
                        self.root = newNode
                    
                for edge in args[0]["edges"]:
                    self.addEdge(edge)

    def addNode(self, node):
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
            node.ontologyclass = nodeobj.get('ontologyclass','')
            node.datatype = nodeobj.get('datatype','')
            node.nodegroup_id = nodeobj.get('nodegroupid','')
            node.branchmetadata_id = nodeobj.get('branchmetadataid','')

        if node.pk == None:
            node.pk = uuid.uuid1()    
        self.nodes[node.pk] = node
        return node

    def addEdge(self, edge):
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
            edge.ontologyproperty = egdeobj.get('ontologyproperty', '')
            edge.branchmetadataid = egdeobj.get('branchmetadataid', '')

        if edge.pk == None:
            edge.pk = uuid.uuid1()  
        self.edges[edge.pk] = edge
        return edge

    def save(self):
        """
        Saves an entity back to the db, returns a DB model instance, not an instance of self

        """

        with transaction.atomic(): 
            for node_id, node in self.nodes.iteritems():
                node.save()

            for edge_id, edge in self.edges.iteritems():
                edge.save()

    def get_nodes_and_edges(self, node):
        """
        Populate a ResourceGraph with the child nodes and edges of parameter: 'node'

        """
        
        self.root = node
        self.addNode(node)

        child_nodes, child_edges = node.get_child_nodes_and_edges()

        for node in child_nodes:
            self.addNode(node)
        for edge in child_edges:
            self.addEdge(edge)

    def append_branch(self, property, nodeid=None, branch_root=None, branchmetadataid=None):  
        """
        Appends a branch onto this graph

        Arguments:
        property -- the property to use when appending the branch

        Keyword Arguments:
        nodeid -- if given will append the branch to this node, if not supplied will 
        append the branch to the root of this graph 

        branch_root -- the root node of the branch you want to append

        branchmetadataid -- get the branch to append based on the branchmetadataid, 
        if given, branch_root takes precedence

        """

        if not branch_root:
            branch_root = models.Node.objects.get(branchmetadata=branchmetadataid, istopnode=True)
        branch_root.istopnode = False
        branch_graph = ResourceGraph(branch_root)
        new_branch = branch_graph.copy()

        with transaction.atomic(): 
            new_branch.save()
            newEdge = models.Edge.objects.create(
                domainnode = (self.nodes[nodeid] if nodeid else self.root),
                rangenode = new_branch.root,
                ontologyproperty = property
            )
            branch_graph.addEdge(newEdge)
        return branch_graph

    def copy(self):
        """
        returns an unsaved copy of self

        """

        copy_of_self = ResourceGraph(self.root.pk)
        for node_id, node in copy_of_self.nodes.iteritems():
            node.pk = uuid.uuid1()

        copy_of_self.nodes = {node.pk:node for node_id, node in copy_of_self.nodes.iteritems()}
        
        for edge_id, edge in copy_of_self.edges.iteritems():
            edge.pk = uuid.uuid1()
            edge.domainnode_id = edge.domainnode.pk
            edge.rangenode_id = edge.rangenode.pk

        copy_of_self.edges = {edge.pk:edge for edge_id, edge in copy_of_self.edges.iteritems()}

        return copy_of_self

    def serialize(self):
        ret = {}
        ret['root'] = self.root
        ret['nodes'] = [node for key, node in self.nodes.iteritems()]
        ret['edges'] = [edge for key, edge in self.edges.iteritems()]
        return ret

    # def get_node_id_from_text(self):
    #     for edge in self.edges:
    #         for node in self.nodes:
    #             if edge['domainnodeid'] == node['name']:
    #                 edge['domainnodeid'] = node['nodeid']
    #             if edge['rangenodeid'] == node['name']:
    #                 edge['rangenodeid'] = node['nodeid']
