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
from django.utils.translation import ugettext as _

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
                self.populate_parent_nodegroups()


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
        nodegroup = models.NodeGroup.objects.create(
            pk=newid
        )
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
            name=_("Top Node"),
            description='',
            istopnode=True,
            ontologyclass=None,
            datatype='semantic',
            nodegroup=nodegroup,
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
                node.nodegroup_id = uuid.UUID(str(node.nodegroup_id))
                try:
                    node.nodegroup = models.NodeGroup.objects.get(pk=node.nodegroup_id)
                except models.NodeGroup.DoesNotExist:
                    node.nodegroup = models.NodeGroup(pk=node.nodegroup_id, cardinality='n')
            else:
                node.nodegroup = None

        node.graph = self.metadata

        if self.metadata.ontology == None:
            node.ontologyclass = None
        if node.pk == None:
            node.pk = uuid.uuid1()
        if node.nodegroup != None:
            self.nodegroups[node.nodegroup.pk] = node.nodegroup
            if hasattr(node, 'cardinality'):
                if node.cardinality != None:
                    self.nodegroups[node.nodegroup.pk].cardinality = node.cardinality
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
        if self.metadata.ontology == None:
            edge.ontologyproperty = None
        self.edges[edge.pk] = edge
        return edge

    def save(self):
        """
        Saves an entity back to the db, returns a DB model instance, not an instance of self

        """


        self.validate()

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
        new_nodegroup_set = set()

        def traverse_tree(tree, current_nodegroup=None):
            if str(tree['node'].nodeid) == str(tree['node'].nodegroup_id):
                 current_nodegroup = models.NodeGroup(
                    pk=tree['node'].nodegroup_id,
                    parentnodegroup=current_nodegroup
                )
            tree['node'].nodegroup = current_nodegroup
            new_nodegroup_set.add(str(current_nodegroup.pk))

            for child in tree['children']:
                traverse_tree(child, current_nodegroup)
            return tree

        traverse_tree(tree)

        #remove any node groups not referenced by the nodes
        old_nodegroup_set = set(list(str(key) for key in self.nodegroups.keys()))
        unused_nodegroup_ids = old_nodegroup_set.difference(new_nodegroup_set)
        for unused_nodegroup_id in unused_nodegroup_ids:
            self.nodegroups.pop(uuid.UUID(str(unused_nodegroup_id)))

        return tree

    def populate_parent_nodegroups(self):
        """
        populates the parent node group of a node group

        """

        for node_id, node in self.nodes.iteritems():
            if str(node_id) == str(node.nodegroup_id) and node.istopnode == False:
                parent_node = self.get_parent_node(node.nodeid)
                self.nodegroups[uuid.UUID(str(node_id))].parentnodegroup = parent_node.nodegroup


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

        newEdge = models.Edge(
            domainnode = (self.nodes[uuid.UUID(str(nodeid))] if nodeid else self.root),
            rangenode = branch_copy.root,
            ontologyproperty = property,
            graph = self.metadata
        )
        branch_copy.add_edge(newEdge)

        for key, node in branch_copy.nodes.iteritems():
            self.add_node(node)
        for key, edge in branch_copy.edges.iteritems():
            self.add_edge(edge)

        self.populate_null_nodegroups()

        if self.metadata.ontology is None:
            branch_copy.clear_ontology_references()

        return branch_copy

    def clear_ontology_references(self):
        """
        removes any references to ontolgoy classes and properties in a graph

        """

        for node_id, node in self.nodes.iteritems():
            node.ontologyclass = None

        for edge_id, edge in self.edges.iteritems():
            edge.ontologyproperty = None

        self.metadata.ontology = None

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

    def update_node(self, node):
        """
        updates a node in the graph

        Arguments:
        node -- a python dictionary representing a node object to be used to update the graph

        """

        node['nodeid'] = uuid.UUID(str(node.get('nodeid')))
        old_node = self.nodes.pop(node['nodeid'], None)
        new_node = self.add_node(node)

        for edge_id, edge in self.edges.iteritems():
            if edge.domainnode_id == new_node.nodeid:
                edge.domainnode = new_node
            if edge.rangenode_id == new_node.nodeid:
                edge.rangenode = new_node
                edge.ontologyproperty = node.get('parentproperty')

        if str(old_node.nodegroup_id) != str(node.get('nodegroup_id', None)):
            self.populate_null_nodegroups()

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

    def get_child_nodes(self, nodeid):
        """
        get the child nodes of a node with the given nodeid

        Arguments:
        nodeid -- the node we want to find the children of

        """

        ret = []
        for edge in self.get_out_edges(nodeid):
            ret.append(edge.rangenode)
            ret.extend(self.get_child_nodes(edge.rangenode.nodeid))
        return ret

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

    def get_valid_domain_ontology_classes(self, nodeid=None):
        """
        gets the ontology properties (and related classes) this graph can have with a parent node

        Keyword Arguments:
        nodeid -- {default=root node id} the id of the node to use as the lookup for valid ontologyclasses

        """
        if self.metadata.ontology is not None:
            source = self.nodes[uuid.UUID(str(nodeid))].ontologyclass if nodeid is not None else self.root.ontologyclass
            ontology_classes = models.OntologyClass.objects.get(source=source, ontology=self.metadata.ontology)
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
        ret['domain_connections'] = self.get_valid_domain_ontology_classes()

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


    def validate(self):
        """
        validates certain aspects of resource graphs according to defined rules:

        - The root node of a "Resource" can only be a semantic node, and must be a collector
        - A node group that has child node groups may not itself be a child node group
        - A node group can only have child node groups if the node group only contains semantic nodes
        - If graph has an ontology, nodes must have classes and edges must have properties that are ontologically valid
        - If the graph has no ontology, nodes and edges should have null values for ontology class and property respectively

        """

        # validates that the top node of a resource graph is semantic and a collector
        if self.root.datatype != 'semantic':
            raise ValidationError("The top node of your resource graph must have a datatype of 'semantic'.")
        if self.root.nodegroup == None:
            raise ValidationError("The top node of your resource graph should be a collector. Hint: check that nodegroup_id of your resource node(s) are not null.")


        
        # validates that a node group that has child node groups is not itself a child node group
        # 20160609 can't implement this without changing our default resource graph --REA
        
        # parentnodegroups = []
        # for nodegroup_id, nodegroup in self.nodegroups.iteritems():
        #     if nodegroup.parentnodegroup:
        #         parentnodegroups.append(nodegroup)

        # for parent in parentnodegroups:
        #     for child in parentnodegroups:
        #         if parent.parentnodegroup_id == child.nodegroupid:
        #             raise ValidationError("A parent node group cannot be a child of another node group.")



        # validates that a all parent node groups that are not root nodegroup only contain semantic nodes.

        for nodegroup_id, nodegroup in self.nodegroups.iteritems():
            if nodegroup.parentnodegroup and nodegroup.parentnodegroup_id != self.root.nodeid:
                for node_id, node in self.nodes.iteritems():
                    if str(node.nodegroup_id) == str(nodegroup.parentnodegroup_id) and node.datatype != 'semantic':
                        raise ValidationError("A parent node group must only contain semantic nodes.")


        # validate that nodes in a resource graph belong to the ontology assigned to the resource graph

        if self.metadata.ontology is not None:
            ontology_classes = self.metadata.ontology.ontologyclasses.values_list('source', flat=True)

            for node_id, node in self.nodes.iteritems():
                if node.ontologyclass not in ontology_classes:
                    raise ValidationError("{0} is not a valid {1} ontology class".format(node.ontologyclass, self.metadata.ontology.ontologyid))
        else:
            for node_id, node in self.nodes.iteritems():
                if node.ontologyclass is not None:
                    raise ValidationError("You have assigned ontology classes to your graph nodes but not assigned an ontology to your graph.")       


class ValidationError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
