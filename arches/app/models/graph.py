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
from copy import copy, deepcopy
from django.db import transaction
from arches.app.models import models
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from django.conf import settings
from django.utils.translation import ugettext as _


class Graph(models.GraphModel):
    """
    Used for mapping complete resource graph objects to and from the database

    """

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(Graph, self).__init__(*args, **kwargs)
        # from models.GraphModel
        # self.graphid = None
        # self.name = ''
        # self.description = ''
        # self.deploymentfile = ''
        # self.author = ''
        # self.deploymentdate = None
        # self.version = ''
        # self.isresource = False
        # self.isactive = False
        # self.iconclass = ''
        # self.subtitle = ''
        # self.ontology = None
        # self.functions = []
        # end from models.GraphModel
        self.root = None
        self.nodes = {}
        self.edges = {}
        self.cards = {}
        self.widgets = {}
        self._nodegroups_to_delete = []

        if args:
            if isinstance(args[0], dict):

                for key, value in args[0].iteritems():
                    if not (key == 'root' or key == 'nodes' or key == 'edges' or key == 'cards' or key == 'functions'):
                        setattr(self, key, value)

                for node in args[0]["nodes"]:
                    nodegroups = {}
                    for nodegroup in args[0]["nodegroups"]:
                        nodegroup = JSONSerializer().serializeToPython(nodegroup)
                        nodegroups[nodegroup["nodegroupid"]] = nodegroup
                    self.add_node(node, nodegroups)

                for edge in args[0]["edges"]:
                    self.add_edge(edge)

                for card in args[0]["cards"]:
                    self.add_card(card)

                if 'functions' in args[0]:
                    for function in args[0]["functions"]:
                        self.add_function(function)

                self.populate_null_nodegroups()

            else:
                if (len(args) == 1 and (isinstance(args[0], basestring) or isinstance(args[0], uuid.UUID))):
                    for key, value in models.GraphModel.objects.get(pk=args[0]).__dict__.iteritems():
                        setattr(self, key, value)

                nodes = self.node_set.all()
                edges = self.edge_set.all()
                cards = self.cardmodel_set.all()

                for node in nodes:
                    self.add_node(node)
                for card in cards:
                    self.add_card(card)
                for edge in edges:
                    edge.domainnode = self.nodes[edge.domainnode.pk]
                    edge.rangenode = self.nodes[edge.rangenode.pk]
                    self.add_edge(edge)

                self.populate_null_nodegroups()

    @staticmethod
    def new(name="", is_resource=False, author=""):
        newid = uuid.uuid1()
        nodegroup = None
        graph = models.GraphModel.objects.create(
            name=name,
            subtitle="",
            author=author,
            description="",
            version="",
            isresource=is_resource,
            isactive=False,
            iconclass="",
            mapfeaturecolor="#FF0000",
            mappointsize=3,
            maplinewidth=1,
            ontology=None
        )
        if not is_resource:
            nodegroup = models.NodeGroup.objects.create(
                pk=newid
            )
            models.CardModel.objects.create(
                nodegroup=nodegroup,
                name=name,
                graph=graph
            )
        root = models.Node.objects.create(
            pk=newid,
            name=_("Top Node"),
            description='',
            istopnode=True,
            ontologyclass=None,
            datatype='semantic',
            nodegroup=nodegroup,
            graph=graph
        )

        return Graph.objects.get(pk=graph.graphid)

    def add_node(self, node, nodegroups=None):
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
            node.config = nodeobj.get('config', None)

            node.nodeid = uuid.UUID(str(node.nodeid))

            if node.nodegroup_id != None and node.nodegroup_id != '':
                node.nodegroup_id = uuid.UUID(str(node.nodegroup_id))
                node.nodegroup = self.get_or_create_nodegroup(nodegroupid=node.nodegroup_id)
                if nodegroups is not None and node.nodegroup_id in nodegroups:
                    node.nodegroup.cardinality = nodegroups[str(node.nodegroup_id)]["cardinality"]
                    node.nodegroup.legacygroupid = nodegroups[str(node.nodegroup_id)]["legacygroupid"]
                    node.nodegroup.parentnodegroupid = nodegroups[str(node.nodegroup_id)]["parentnodegroup_id"]
            else:
                node.nodegroup = None

        node.graph = self

        if self.ontology == None:
            node.ontologyclass = None
        if node.pk == None:
            node.pk = uuid.uuid1()
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
            edge.rangenode = self.nodes[uuid.UUID(str(egdeobj.get('rangenode_id')))]
            edge.domainnode = self.nodes[uuid.UUID(str(egdeobj.get('domainnode_id')))]
            edge.ontologyproperty = egdeobj.get('ontologyproperty', '')

        edge.graph = self

        if edge.pk == None:
            edge.pk = uuid.uuid1()
        if self.ontology == None:
            edge.ontologyproperty = None
        self.edges[edge.pk] = edge
        return edge

    def add_card(self, card):
        """
        Adds a card to this graph

        Arguments:
        node -- a dictionary representing a Card instance or an actual models.CardModel instance

        """

        if not isinstance(card, models.CardModel):
            cardobj = card.copy()
            card = models.CardModel()
            card.cardid = cardobj.get('cardid', None)
            card.name = cardobj.get('name', '')
            card.description = cardobj.get('description','')
            card.instructions = cardobj.get('instructions','')
            card.helptext = cardobj.get('helptext','')
            card.nodegroup_id = uuid.UUID(str(cardobj.get('nodegroup_id','')))
            card.nodegroup = self.get_or_create_nodegroup(nodegroupid=card.nodegroup_id)

        card.graph = self

        if card.pk == None:
            card.pk = uuid.uuid1()

        self.cards[card.pk] = card

        widgets = list(card.cardxnodexwidget_set.all())
        for widget in widgets:
            self.widgets[widget.pk] = widget

        return card

    def add_function(self, function):
        """
        Adds a card to this graph

        Arguments:
        node -- a dictionary representing a Card instance or an actual models.CardModel instance

        """

        if not isinstance(function, models.FunctionXGraph):
            functionobj = function.copy()
            function = models.FunctionXGraph()
            function.fuction_id = functionobj.functionid
            function.config = functionobj.config

        function.graph = self

        return function

    def save(self):
        """
        Saves an a graph and it's nodes, edges, and nodegroups back to the db
        creates associated card objects if any of the nodegroups don't already have a card

        """

        self.validate()

        with transaction.atomic():
            super(Graph, self).save()

            for nodegroup in self.get_nodegroups():
                nodegroup.save()

            for node in self.nodes.itervalues():
                node.save()

            for edge in self.edges.itervalues():
                edge.save()

            for card in self.cards.itervalues():
                card.save()

            for widget in self.widgets.itervalues():
                widget.save()

            for nodegroup in self._nodegroups_to_delete:
                nodegroup.delete()
            self._nodegroups_to_delete = []

        return self

    def delete(self):
        with transaction.atomic():
            for nodegroup in self.get_nodegroups():
                nodegroup.delete()

            for edge in self.edges.itervalues():
                edge.delete()

            for node in self.nodes.itervalues():
                node.delete()

            for card in self.cards.itervalues():
                card.delete()

            for widget in self.widgets.itervalues():
                widget.delete()

            super(Graph, self).delete()

    def get_tree(self, root=None):
        """
        returns a tree based representation of this graph

        Keyword Arguments:
        root -- the node from which to root the tree, defaults to the root node of this graph

        """

        tree = {
            'node': root if root else self.root,
            'children': [],
            'parent_edge': None
        }

        def find_child_edges(tree):
            for edge_id, edge in self.edges.iteritems():
                if edge.domainnode == tree['node']:
                    tree['children'].append(find_child_edges({
                        'node': edge.rangenode,
                        'children':[],
                        'parent_edge': edge
                    }))

            return tree

        return find_child_edges(tree)

    def populate_null_nodegroups(self):
        """
        populates any blank nodegroup ids of the nodes in this graph with the nearest parent node

        """

        tree = self.get_tree()

        def traverse_tree(tree, current_nodegroup=None):
            if tree['node'].is_collector:
                nodegroup = self.get_or_create_nodegroup(nodegroupid=tree['node'].nodegroup_id)
                nodegroup.parentnodegroup = current_nodegroup
                current_nodegroup = nodegroup

            tree['node'].nodegroup = current_nodegroup

            for child in tree['children']:
                traverse_tree(child, current_nodegroup)
            return tree

        traverse_tree(tree)

        return tree

    def append_branch(self, property, nodeid=None, graphid=None, skip_validation=False):
        """
        Appends a branch onto this graph

        Arguments:
        property -- the property to use when appending the branch

        Keyword Arguments:
        nodeid -- if given will append the branch to this node, if not supplied will
        append the branch to the root of this graph

        graphid -- get the branch to append based on the graphid

        skip_validation -- don't validate the resultant graph (post append), defaults to False

        """

        branch_graph = Graph(graphid)
        nodeToAppendTo = self.nodes[uuid.UUID(str(nodeid))] if nodeid else self.root

        if skip_validation or self.can_append(branch_graph, nodeToAppendTo):
            branch_copy = branch_graph.copy()
            branch_copy.root.istopnode = False

            newEdge = models.Edge(
                domainnode = nodeToAppendTo,
                rangenode = branch_copy.root,
                ontologyproperty = property,
                graph = self
            )
            branch_copy.add_edge(newEdge)

            for node in branch_copy.nodes.itervalues():
                self.add_node(node)
            for card in branch_copy.get_cards():
                self.add_card(card)
            for edge in branch_copy.edges.itervalues():
                self.add_edge(edge)
            for widget in branch_copy.widgets.itervalues():
                self.widgets[widget.pk] = widget

            self.populate_null_nodegroups()

            if self.ontology is None:
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

        self.ontology = None

    def copy(self):
        """
        returns an unsaved copy of self

        """

        new_nodegroups = {}

        copy_of_self = deepcopy(self)
        # returns a list of node ids sorted by nodes that are collector nodes first and then others last
        node_ids = sorted(copy_of_self.nodes, key=lambda node_id: copy_of_self.nodes[node_id].is_collector, reverse=True)

        copy_of_self.pk = uuid.uuid1()
        node_map = {}
        card_map = {}
        for node_id in node_ids:
            node = copy_of_self.nodes[node_id]
            if node == self.root:
                copy_of_self.root = node
            node.graph = copy_of_self
            is_collector = node.is_collector
            node.pk = uuid.uuid1()
            node_map[node_id] = node.pk
            if is_collector:
                old_nodegroup_id = node.nodegroup_id
                node.nodegroup = models.NodeGroup(pk=node.pk, cardinality=node.nodegroup.cardinality)
                for card in copy_of_self.cards.itervalues():
                    if str(card.nodegroup_id) == str(old_nodegroup_id):
                        new_id = uuid.uuid1()
                        card_map[card.pk] = new_id
                        card.pk = new_id
                        card.nodegroup = node.nodegroup
                        card.graph = copy_of_self
            else:
                node.nodegroup = None

        for widget in copy_of_self.widgets.itervalues():
            widget.pk = uuid.uuid1()
            widget.node_id = node_map[widget.node_id]
            widget.card_id = card_map[widget.card_id]

        copy_of_self.populate_null_nodegroups()

        copy_of_self.nodes = {node.pk:node for node_id, node in copy_of_self.nodes.iteritems()}

        for edge_id, edge in copy_of_self.edges.iteritems():
            edge.pk = uuid.uuid1()
            edge.graph = copy_of_self
            edge.domainnode_id = edge.domainnode.pk
            edge.rangenode_id = edge.rangenode.pk

        copy_of_self.edges = {edge.pk:edge for edge_id, edge in copy_of_self.edges.iteritems()}

        return copy_of_self

    def move_node(self, nodeid, property, newparentnodeid, skip_validation=False):
        """
        move a node and it's children to a different location within this graph

        Arguments:
        nodeid -- the id of node being moved

        property -- the property value to conect the node to it's new parent nodegroup

        newparentnodeid -- the parent node id that the node is being moved to

        skip_validation -- don't validate the resultant graph (post move), defaults to False

        """

        ret = {'nodes':[], 'edges':[]}
        nodegroup = None
        node = self.nodes[uuid.UUID(str(nodeid))]

        graph_dict = self.serialize()
        graph_dict['nodes'] = []
        graph_dict['edges'] = []
        graph_dict['cards'] = []
        def traverse_tree(tree):
            graph_dict['nodes'].append(tree['node'])
            for child in tree['children']:
                graph_dict['edges'].append({'domainnode_id':tree['node']['nodeid'],'rangenode_id':child['node']['nodeid']})
                traverse_tree(child)
        tree = JSONSerializer().serializeToPython(self.get_tree(node))
        tree['node']['istopnode'] = True
        traverse_tree(tree)

        if skip_validation or self.can_append(Graph(graph_dict), self.nodes[uuid.UUID(str(newparentnodeid))]):
            if not node.is_collector:
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
        old_node = self.nodes.pop(node['nodeid'])
        new_node = self.add_node(node)

        for edge_id, edge in self.edges.iteritems():
            if edge.domainnode_id == new_node.nodeid:
                edge.domainnode = new_node
            if edge.rangenode_id == new_node.nodeid:
                edge.rangenode = new_node
                edge.ontologyproperty = node.get('parentproperty')

        self.populate_null_nodegroups()

        # new_node will always have a nodegroup id even it if was set to None becuase populate_null_nodegroups
        # will populate the nodegroup id with the parent nodegroup
        # add/remove a card if a nodegroup was added/removed
        if new_node.nodegroup_id != old_node.nodegroup_id:
            if new_node.is_collector:
                # add a card
                self.add_card(models.CardModel(name=new_node.name, nodegroup=new_node.nodegroup))
            else:
                self._nodegroups_to_delete = [old_node.nodegroup]
                # remove a card
                self.cards = {
                    card_id: card for card_id, card in self.cards.iteritems()
                        if card.nodegroup_id != old_node.nodegroup_id
                }

        return self

    def delete_node(self, node=None):
        """
        deletes a node and all if it's children from a graph

        Arguments:
        node -- a node id or Node model to delete from the graph

        """

        if node is not None:
            if not isinstance(node, models.Node):
                node = self.nodes[uuid.UUID(str(node))]

            nodes = []
            edges = []
            nodegroups = []

            tree = self.get_tree(root=node)
            def traverse_tree(tree):
                nodes.append(tree['node'])
                if tree['node'].is_collector:
                    nodegroups.append(tree['node'].nodegroup)
                for child in tree['children']:
                    edges.append(child['parent_edge'])
                    traverse_tree(child)
            traverse_tree(tree)

            with transaction.atomic():
                [nodegroup.delete() for nodegroup in nodegroups]
                [edge.delete() for edge in edges]
                [node.delete() for node in nodes]

    def can_append(self, graphToAppend, nodeToAppendTo):
        """
        can_append - test to see whether or not a graph can be appened to this graph at a specific location

        returns true if the graph can be appended, false otherwise

        Arguments:
        graphToAppend -- the Graph to test appending on to this graph
        nodeToAppendTo -- the node from which to append the graph

        """

        typeOfGraphToAppend = graphToAppend.is_type()

        found = False
        if self.ontology is not None and graphToAppend.ontology is None:
            raise ValidationError(_('The graph you wish to append needs to define an ontology'))

        if self.ontology is not None and graphToAppend.ontology is not None:
            for domain_connection in graphToAppend.get_valid_domain_ontology_classes():
                for ontology_class in domain_connection['ontology_classes']:
                    if ontology_class == nodeToAppendTo.ontologyclass:
                        found = True
                        break

                if found:
                    break

            if not found:
                raise ValidationError(_('Ontology rules don\'t allow this graph to be appended'))
        if self.isresource:
            if(nodeToAppendTo != self.root):
                raise ValidationError(_('Can\'t append a graph to a resource except at the root'))
            else:
                if typeOfGraphToAppend == 'undefined':
                    raise ValidationError(_('Can\'t append an undefined graph to a resource graph'))
        else: # self graph is a Graph
            graph_type = self.is_type()
            if graph_type == 'undefined':
                raise ValidationError(_('Can\'t append any graph to an undefined graph'))
            elif graph_type == 'card':
                if typeOfGraphToAppend == 'card':
                    if nodeToAppendTo == self.root:
                        if not self.is_group_semantic(nodeToAppendTo):
                            raise ValidationError(_('Can only append a card type graph to a semantic group'))
                    else:
                        raise ValidationError(_('Can only append to the root of the graph'))
                elif typeOfGraphToAppend == 'card_collector':
                    raise ValidationError(_('Can\'t append a card collector type graph to a card type graph'))
            elif graph_type == 'card_collector':
                if typeOfGraphToAppend == 'card_collector':
                    raise ValidationError(_('Can\'t append a card collector type graph to a card collector type graph'))
                if self.is_node_in_child_group(nodeToAppendTo):
                    if typeOfGraphToAppend == 'card':
                        raise ValidationError(_('Can only append an undefined type graph to a child within a card collector type graph'))
        return True

    def is_type(self):
        """
        does this graph contain a card, a collection of cards, or no cards

        returns either 'card', 'card_collector', or 'undefined'

        """

        count = self.get_nodegroups()

        if len(count) == 0:
            return 'undefined'
        elif len(count) == 1:
            return 'card'
        else:
            return 'card_collector'

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

    def is_node_in_child_group(self, node):
        """
        test to see if the node is in a group that is a child to another group

        return true if the node is in a child group, false otherwise

        Arguments:
        node -- the node to test

        """

        hasParentGroup = False
        nodegroup_id = node.nodegroup_id
        if not nodegroup_id:
            return False

        for node in self.get_parent_nodes_and_edges(node)['nodes']:
            if node.nodegroup is not None and node.nodegroup_id != nodegroup_id:
                hasParentGroup = True

        return hasParentGroup

    def get_parent_nodes_and_edges(self, node):
        """
        given a node, get all the parent nodes and edges

        returns an object with a list of nodes and edges

        Arguments:
        node -- the node from which to get the node's parents

        """

        nodes = []
        edges = []
        for edge in self.edges.itervalues():
            if edge.rangenode_id == node.nodeid:
                edges.append(edge)
                nodes.append(edge.domainnode)

                nodesAndEdges = self.get_parent_nodes_and_edges(edge.domainnode)
                nodes.extend(nodesAndEdges['nodes'])
                edges.extend(nodesAndEdges['edges'])

        return {
            'nodes': nodes,
            'edges': edges
        }

    def is_group_semantic(self, node):
        """
        test to see if all the nodes in a group are semantic

        returns true if the group contains only semantic nodes, otherwise false

        Arguments:
        node -- the node to use as a basis of finding the group

        """

        for node in self.get_grouped_nodes(node):
            if node.datatype != 'semantic':
                return False

        return True

    def get_grouped_nodes(self, node):
        """
        given a node, get any other nodes that share the same group

        returns a list of nodes

        Arguments:
        node -- the node to use as a basis of finding the group

        """

        ret = []
        nodegroup_id = node.nodegroup_id;
        if (nodegroup_id == ''):
            return [node];

        for node in self.nodes.itervalues():
            if node.nodegroup_id == nodegroup_id:
                ret.append(node)

        return ret

    def get_valid_domain_ontology_classes(self, nodeid=None):
        """
        gets the ontology properties (and related classes) this graph can have with a parent node

        Keyword Arguments:
        nodeid -- {default=root node id} the id of the node to use as the lookup for valid ontologyclasses

        """
        if self.ontology is not None:
            source = self.nodes[uuid.UUID(str(nodeid))].ontologyclass if nodeid is not None else self.root.ontologyclass
            ontology_classes = models.OntologyClass.objects.get(source=source, ontology=self.ontology)
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
        if nodeid and self.ontology_id is not None:
            parent_node = self.get_parent_node(nodeid)
            out_edges = self.get_out_edges(nodeid)

            ontology_classes = set()
            if len(out_edges) > 0:
                for edge in out_edges:
                    for ontology_property in models.OntologyClass.objects.get(source=edge.rangenode.ontologyclass, ontology_id=self.ontology_id).target['up']:
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
                range_ontologies = models.OntologyClass.objects.get(source=parent_node.ontologyclass, ontology_id=self.ontology_id).target['down']
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
                        'ontology_classes':models.OntologyClass.objects.values_list('source', flat=True).filter(ontology_id=self.ontology_id)
                    }]
                else:
                    # if no parent node then just use the list of ontology classes from above, there will be no properties to return
                    ret = [{
                        'ontology_property':'',
                        'ontology_classes':list(ontology_classes)
                    }]

        return ret

    def get_nodegroups(self, nodegroupid=None):
        """
        get the nodegroups associated with this graph

        """

        nodegroups =set()
        for node in self.nodes.itervalues():
            if node.is_collector:
                nodegroups.add(node.nodegroup)
        for card in self.cards.itervalues():
            nodegroups.add(card.nodegroup)
        return list(nodegroups)

    def get_or_create_nodegroup(self, nodegroupid):
        """
        get a nodegroup from an id by first looking through the nodes and cards associated with this graph.
        if not found then get the nodegroup instance from the database, otherwise return a new instance of a nodegroup

        Keyword Arguments

        nodegroupid -- return a nodegroup with this id

        """

        for nodegroup in self.get_nodegroups():
            if str(nodegroup.nodegroupid) == str(nodegroupid):
                return nodegroup
        try:
            return models.NodeGroup.objects.get(pk=nodegroupid)
        except models.NodeGroup.DoesNotExist:
            return models.NodeGroup(pk=nodegroupid)

    def get_root_nodegroup(self):
        """
        gets the top level nodegroup (the first nodegroup that doesn't have a parentnodegroup)

        """

        for nodegroup in self.get_nodegroups():
            if nodegroup.parentnodegroup is None:
                return nodegroup

    def get_root_card(self):
        """
        gets the top level card/card container

        """

        for card in self.cards.itervalues():
            if card.nodegroup.parentnodegroup is None:
                return card

    def get_cards(self):
        """
        get the card data (if any) associated with this graph

        """

        cards = []
        for card in self.cards.itervalues():
            if self.isresource:
                if not card.name:
                    card.name = self.nodes[card.nodegroup.pk].name
                if not card.description:
                    card.description = self.nodes[card.nodegroup.pk].description
            else:
                if card.nodegroup.parentnodegroup is None:
                    card.name = self.name
                    card.description = self.description
                else:
                    if not card.name:
                        card.name = self.nodes[card.nodegroup.pk].name
                    if not card.description:
                        card.description = self.nodes[card.nodegroup.pk].description

            cards.append(card)

        return cards

    def serialize(self):
        """
        serialize to a different form then used by the internal class structure

        used to append additional values (like parent ontology properties) that
        internal objects (like models.Nodes) don't support

        """

        ret = JSONSerializer().handle_model(self)
        ret['root'] = self.root
        ret['cards'] = self.get_cards()
        ret['nodegroups'] = self.get_nodegroups()
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

        if self.isresource == True:
            if self.root.is_collector == True:
                raise ValidationError(_("The top node of your resource graph: {0} needs to be a collector. Hint: check that nodegroup_id of your resource node(s) are not null.".format(self.root.name)))
            if self.root.datatype != 'semantic':
                raise ValidationError(_("The top node of your resource graph must have a datatype of 'semantic'."))
        else:
            if self.root.is_collector == False:
                if len(self.nodes) > 1:
                    raise ValidationError(_("If your graph contains more than one node and is not a resource the root must be a collector."))


        # validates that a node group that has child node groups is not itself a child node group
        # 20160609 can't implement this without changing our default resource graph --REA

        # parentnodegroups = []
        # for nodegroup in self.get_nodegroups():
        #     if nodegroup.parentnodegroup:
        #         parentnodegroups.append(nodegroup)

        # for parent in parentnodegroups:
        #     for child in parentnodegroups:
        #         if parent.parentnodegroup_id == child.nodegroupid:
        #             raise ValidationError(_("A parent node group cannot be a child of another node group."))



        # validates that a all parent node groups that are not root nodegroup only contain semantic nodes.

        for nodegroup in self.get_nodegroups():
            if nodegroup.parentnodegroup and nodegroup.parentnodegroup_id != self.root.nodeid:
                for node_id, node in self.nodes.iteritems():
                    if str(node.nodegroup_id) == str(nodegroup.parentnodegroup_id) and node.datatype != 'semantic':
                        raise ValidationError(_("A parent node group must only contain semantic nodes."))


        # validate that nodes in a resource graph belong to the ontology assigned to the resource graph

        if self.ontology is not None:
            ontology_classes = self.ontology.ontologyclasses.values_list('source', flat=True)

            for node_id, node in self.nodes.iteritems():
                if node.ontologyclass not in ontology_classes:
                    raise ValidationError(_("{0} is not a valid {1} ontology class".format(node.ontologyclass, self.ontology.ontologyid)))
        else:
            for node_id, node in self.nodes.iteritems():
                if node.ontologyclass is not None:
                    raise ValidationError(_("You have assigned ontology classes to your graph nodes but not assigned an ontology to your graph."))


class ValidationError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
