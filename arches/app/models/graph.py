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
from django.conf import settings

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
                metadata_dict = args[0]["metadata"]
                for key, value in metadata_dict.iteritems():
                    setattr(self.metadata, key, value)

                for node in args[0]["nodes"]:
                    newNode = self.add_node(node)

                for edge in args[0]["edges"]:
                    self.add_edge(edge)

                self.populate_null_nodegroups()

            else:
                if (isinstance(args[0], basestring) or
                   isinstance(args[0], uuid.UUID)):
                    self.metadata = models.Graph.objects.get(pk=args[0])
                elif isinstance(args[0], models.Graph):
                    self.metadata = args[0]
                elif isinstance(args[0], models.Node):
                    self.metadata = args[0].graph
                nodes = self.metadata.node_set.all()
                edges = self.metadata.edge_set.all()
                for node in nodes:
                    self.add_node(node)
                for edge in edges:
                    edge.domainnode = self.nodes[edge.domainnode.pk]
                    edge.rangenode = self.nodes[edge.rangenode.pk]
                    self.add_edge(edge)

    @staticmethod
    def new(name="",is_resource=False,author=""):
        newid = uuid.uuid1()
        metadata = models.Graph.objects.create(
            name=name,
            subtitle="",
            author=author,
            description="",
            version="",
            isresource=is_resource,
            isactive=False,
            iconclass="",
            ontology=None
        )
        root = models.Node.objects.create(
            pk=newid,
            name=name,
            description='',
            istopnode=True,
            ontologyclass=None,
            datatype='semantic',
            nodegroup=None,
            graph=metadata
        )

        return Graph(metadata)

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
            node.ontologyclass = nodeobj.get('ontologyclass','')
            node.datatype = nodeobj.get('datatype','')
            node.nodegroup_id = nodeobj.get('nodegroup_id','')
            node.validations.set(nodeobj.get('validations', []))

            if node.nodegroup_id != None and node.nodegroup_id != '':
                try:
                    node.nodegroup = models.NodeGroup.objects.get(pk=uuid.UUID(node.nodegroup_id))
                except models.NodeGroup.DoesNotExist:
                    node.nodegroup = models.NodeGroup(pk=uuid.UUID(node.nodegroup_id), cardinality='n')
            else:
                node.nodegroup = None

        node.graph = self.metadata

        if node.pk == None:
            node.pk = uuid.uuid1()
        if node.nodegroup != None:
            self.nodegroups[node.nodegroup.pk] = node.nodegroup
        if node.istopnode:
            self.root = node
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
            edge.ontologyproperty = egdeobj.get('ontologyproperty', '')

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

    def delete(self):
        with transaction.atomic():
            for edge_id, edge in self.edges.iteritems():
                edge.delete()

            for node_id, node in self.nodes.iteritems():
                node.delete()

            for nodegroup_id, nodegroup in self.nodegroups.iteritems():
                nodegroup.delete()

            self.metadata.delete()

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
                ontologyproperty = property,
                graph = self.metadata
            )
            branch_copy.add_edge(newEdge)
        for key, node in branch_copy.nodes.iteritems():
            if self.metadata.ontology_id is None:
                node.ontologyclass = None
            self.add_node(node)
        for key, edge in branch_copy.edges.iteritems():
            if self.metadata.ontology_id is None:
                edge.ontologyproperty = None
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

    def toggle_is_collector(self, node):
        nodes, edges = node.get_child_nodes_and_edges()
        collectors = [node_ for node_ in nodes if node_.is_collector()]
        node_ids = [id_node.nodeid for id_node in nodes]
        group_nodes = [node_ for node_ in nodes if (node_.nodegroup_id not in node_ids)]
        if node.istopnode:
            parent_group = None
        else:
            edge = models.Edge.objects.get(rangenode_id=node.pk)
            parent_group = edge.domainnode.nodegroup

        if not node.is_collector():
            new_group, created = models.NodeGroup.objects.get_or_create(nodegroupid=node.pk, defaults={'cardinality': 'n', 'legacygroupid': None, 'parentnodegroup': None})
            new_group.parentnodegroup = parent_group
            parent_group = new_group
            self.nodegroups[new_group.pk] = new_group
        else:
            new_group = parent_group

        for collector in collectors:
            collector.nodegroup.parentnodegroup = parent_group
            self.nodegroups[collector.nodegroup.pk] = collector.nodegroup

        for group_node in group_nodes:
            group_node.nodegroup = new_group
            self.nodes[group_node.pk] = group_node
        node.nodegroup = new_group

    def update_node(self, node):
        """
        updates a node in the graph

        Arguments:
        node -- the node object to update

        """

        node['nodeid'] = uuid.UUID(node.get('nodeid'))
        new_nodegroup_id = node.get('nodegroup_id', None)
        old_node = self.nodes[node['nodeid']]
        old_nodegroup_id = unicode(old_node.nodegroup_id) if old_node.nodegroup_id is not None else None
        node['nodegroup_id'] = old_nodegroup_id
        self.nodes.pop(node['nodeid'], None)
        new_node = self.add_node(node)

        for edge_id, edge in self.edges.iteritems():
            if edge.domainnode_id == new_node.nodeid:
                edge.domainnode = new_node
            if edge.rangenode_id == new_node.nodeid:
                edge.rangenode = new_node
                edge.ontologyproperty = node.get('parentproperty')

        if old_nodegroup_id != new_nodegroup_id:
            self.toggle_is_collector(new_node)

        return self

    def get_parent_node(self, nodeid):
        """
        get the parent node of a node with the given nodeid

        Arguments:
        nodeid -- the node we want to find the parent of

        """

        if str(self.root.nodeid) == str(nodeid):
            return None
        for edge_id, edge in self.edges.iteritems():
            if str(edge.rangenode_id) == str(nodeid):
                return edge.domainnode
        return None

    def get_out_edges(self, nodeid):
        """
        get all the edges of a node with the given nodeid where that node is the domainnode

        Arguments:
        nodeid -- the nodeid of the node we want to find the edges of

        """

        ret = []
        for edge_id, edge in self.edges.iteritems():
            if str(edge.domainnode_id) == str(nodeid):
                ret.append(edge)
        return ret

    def get_valid_domain_connections(self):
        """
        gets the ontology properties (and related classes) this graph can have with a parent node

        """
        if self.root.ontologyclass is not None:
            ontology_classes = models.OntologyClass.objects.get(source=self.root.ontologyclass)
            return ontology_classes.target['up']
        else:
            return []

    def get_valid_ontology_classes(self, nodeid=None):
        """
        get possible ontology properties (and related classes) a node with the given nodeid can have
        taking into consideration it's current position in the graph

        Arguments:
        nodeid -- the id of the node in question

        """

        ret = []
        if nodeid and self.metadata.ontology_id is not None:
            parent_node = self.get_parent_node(nodeid)
            out_edges = self.get_out_edges(nodeid)

            ontology_classes = set()
            if len(out_edges) > 0:
                for edge in out_edges:
                    for ontology_property in models.OntologyClass.objects.get(source=edge.rangenode.ontologyclass, ontology_id=self.metadata.ontology_id).target['up']:
                        if edge.ontologyproperty == ontology_property['ontology_property']:
                            if len(ontology_classes) == 0:
                                ontology_classes = set(ontology_property['ontology_classes'])
                            else:
                                ontology_classes = ontology_classes.intersection(set(ontology_property['ontology_classes']))

                            if len(ontology_classes) == 0:
                                break

            # get a list of properties (and corresponding classes) that could be used to relate to my parent node
            # limit the list of properties based on the intersection between the property's classes and the list of
            # ontology classes we found above
            if parent_node:
                range_ontologies = models.OntologyClass.objects.get(source=parent_node.ontologyclass, ontology_id=self.metadata.ontology_id).target['down']
                if len(out_edges) == 0:
                    return range_ontologies
                else:
                    for ontology_property in range_ontologies:
                        ontology_property['ontology_classes'] = list(set(ontology_property['ontology_classes']).intersection(ontology_classes))

                        if len(ontology_property['ontology_classes']) > 0:
                            ret.append(ontology_property)

            else:
                # if a brand new resource
                if len(out_edges) == 0:
                    ret = [{
                        'ontology_property':'',
                        'ontology_classes':models.OntologyClass.objects.values_list('source', flat=True).filter(ontology_id=self.metadata.ontology_id)
                    }]
                else:
                    # if no parent node then just use the list of ontology classes from above, there will be no properties to return
                    ret = [{
                        'ontology_property':'',
                        'ontology_classes':list(ontology_classes)
                    }]

        return ret

    def serialize(self):
        """
        serialize to a different form then used by the internal class structure

        used to append additional values (like parent ontology properties) that
        internal objects (like models.Nodes) don't support

        """

        ret = {}
        ret['root'] = self.root;
        ret['metadata'] = self.metadata
        ret['nodegroups'] = [nodegroup for key, nodegroup in self.nodegroups.iteritems()]
        ret['domain_connections'] = self.get_valid_domain_connections()

        ret['edges'] = [edge for key, edge in self.edges.iteritems()]
        ret['nodes'] = []
        parentproperties = {
            self.root.nodeid: ''
        }
        for edge_id, edge in self.edges.iteritems():
            parentproperties[edge.rangenode_id] = edge.ontologyproperty
        for key, node in self.nodes.iteritems():
            nodeobj = JSONSerializer().serializeToPython(node)
            nodeobj['parentproperty'] = parentproperties[node.nodeid]
            ret['nodes'].append(nodeobj)

        return ret
