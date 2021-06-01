"""
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
"""

import json
import logging
import pyprind
import uuid
from copy import copy, deepcopy
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.utils import IntegrityError
from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.search.search_engine_factory import SearchEngineFactory
from django.utils.translation import ugettext as _
from pyld.jsonld import compact, JsonLdError

logger = logging.getLogger(__name__)

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
        # self.color = ''
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
        self._functions = []
        self._card_constraints = []
        self._constraints_x_nodes = []
        self.temp_node_name = _("New Node")

        if args:
            if isinstance(args[0], dict):

                for key, value in args[0].items():
                    if key not in ("root", "nodes", "edges", "cards", "functions", "is_editable"):
                        setattr(self, key, value)

                nodegroups = dict((item["nodegroupid"], item) for item in args[0]["nodegroups"])
                for node in args[0]["nodes"]:
                    self.add_node(node, nodegroups)

                for edge in args[0]["edges"]:
                    self.add_edge(edge)

                for card in args[0]["cards"]:
                    self.add_card(card)

                def check_default_configs(default_configs, configs):
                    if default_configs is not None:
                        if configs is None:
                            configs = {}
                        for default_key in default_configs:
                            if default_key not in configs:
                                configs[default_key] = default_configs[default_key]
                    return configs

                if "functions_x_graphs" in args[0]:
                    for function in args[0]["functions_x_graphs"]:
                        function_x_graph_config = function["config"]
                        default_config = models.Function.objects.get(functionid=function["function_id"]).defaultconfig
                        function["config"] = check_default_configs(default_config, function_x_graph_config)

                        self.add_function(function)

                self.populate_null_nodegroups()

            else:
                if len(args) == 1 and (isinstance(args[0], str) or isinstance(args[0], uuid.UUID)):
                    for key, value in models.GraphModel.objects.get(pk=args[0]).__dict__.items():
                        setattr(self, key, value)

                nodes = self.node_set.all()
                edges = self.edge_set.all()
                cards = self.cardmodel_set.all()
                edge_dicts = json.loads(JSONSerializer().serialize(edges))
                node_lookup = {}
                edge_lookup = {edge["edgeid"]: edge for edge in edge_dicts}
                for node in nodes:
                    self.add_node(node)
                    node_lookup[str(node.nodeid)] = node
                for card in cards:
                    self.add_card(card)
                for edge in edges:
                    edge_dict = edge_lookup[str(edge.edgeid)]
                    edge.domainnode = node_lookup[edge_dict["domainnode_id"]]
                    edge.rangenode = node_lookup[edge_dict["rangenode_id"]]
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
            isactive=not is_resource,
            iconclass="",
            ontology=None,
            slug=None,
        )
        if not is_resource:
            nodegroup = models.NodeGroup.objects.create(pk=newid)
            models.CardModel.objects.create(nodegroup=nodegroup, name=name, graph=graph)
        root = models.Node.objects.create(
            pk=newid,
            name=_("Top Node"),
            description="",
            istopnode=True,
            ontologyclass=None,
            datatype="semantic",
            nodegroup=nodegroup,
            graph=graph,
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
            node.nodeid = nodeobj.get("nodeid", None)
            node.name = nodeobj.get("name", "")
            node.description = nodeobj.get("description", "")
            node.istopnode = nodeobj.get("istopnode", "")
            node.ontologyclass = nodeobj.get("ontologyclass", "")
            node.datatype = nodeobj.get("datatype", "")
            node.nodegroup_id = nodeobj.get("nodegroup_id", "")
            node.config = nodeobj.get("config", None)
            node.issearchable = nodeobj.get("issearchable", True)
            node.isrequired = nodeobj.get("isrequired", False)
            node.exportable = nodeobj.get("exportable", False)
            node.fieldname = nodeobj.get("fieldname", "")

            node.nodeid = uuid.UUID(str(node.nodeid))

            if node.nodegroup_id is not None and node.nodegroup_id != "":
                node.nodegroup_id = uuid.UUID(str(node.nodegroup_id))
                node.nodegroup = self.get_or_create_nodegroup(nodegroupid=node.nodegroup_id)
                if nodegroups is not None and str(node.nodegroup_id) in nodegroups:
                    node.nodegroup.cardinality = nodegroups[str(node.nodegroup_id)]["cardinality"]
                    node.nodegroup.legacygroupid = nodegroups[str(node.nodegroup_id)]["legacygroupid"]
                    node.nodegroup.parentnodegroupid = nodegroups[str(node.nodegroup_id)]["parentnodegroup_id"]
            else:
                node.nodegroup = None

        node.graph = self

        if self.ontology is None:
            node.ontologyclass = None
        if node.pk is None:
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
            edge.edgeid = egdeobj.get("edgeid", None)
            edge.rangenode = self.nodes[uuid.UUID(str(egdeobj.get("rangenode_id")))]
            edge.domainnode = self.nodes[uuid.UUID(str(egdeobj.get("domainnode_id")))]
            edge.ontologyproperty = egdeobj.get("ontologyproperty", "")

        edge.graph = self

        if edge.pk is None:
            edge.pk = uuid.uuid1()
        if self.ontology is None:
            edge.ontologyproperty = None
        self.edges[edge.pk] = edge
        return edge

    def add_card_contraint(self, constraint, card):
        unique_to_all = constraint.get("uniquetoallinstances", False)
        constraint_model = models.ConstraintModel()
        constraint_model.constraintid = constraint.get("constraintid", None)
        constraint_model.uniquetoallinstances = constraint.get("uniquetoallinstances", False)
        constraint_model.card = card
        self._card_constraints.append(constraint_model)
        for nodeid in constraint.get("nodes", []):
            constraint_x_node = {"constraint": constraint_model, "node": nodeid}
            self._constraints_x_nodes.append(constraint_x_node)

    def add_card(self, card):
        """
        Adds a card to this graph

        Arguments:
        card -- a dictionary representing a Card instance or an actual models.CardModel instance

        """
        if not isinstance(card, models.CardModel):
            cardobj = card.copy()
            card = models.CardModel()
            card.cardid = cardobj.get("cardid", None)
            card.name = cardobj.get("name", "")
            card.description = cardobj.get("description", "")
            card.instructions = cardobj.get("instructions", "")
            card.helpenabled = cardobj.get("helpenabled", "")
            card.helptitle = cardobj.get("helptitle", "")
            card.helptext = cardobj.get("helptext", "")
            card.cssclass = cardobj.get("cssclass", "")
            card.active = cardobj.get("active", "")
            card.visible = cardobj.get("visible", "")
            card.sortorder = cardobj.get("sortorder", "")
            card.component_id = cardobj.get("component_id", uuid.UUID("f05e4d3a-53c1-11e8-b0ea-784f435179ea"))
            card.nodegroup_id = uuid.UUID(str(cardobj.get("nodegroup_id", "")))
            card.nodegroup = self.get_or_create_nodegroup(nodegroupid=card.nodegroup_id)
            card.config = cardobj.get("config", None)
            constraints = cardobj.get("constraints", "")
            for constraint in constraints:
                self.add_card_contraint(constraint, card)

        card.graph = self

        if card.pk is None:
            card.pk = uuid.uuid1()

        self.cards[card.pk] = card

        widgets = list(card.cardxnodexwidget_set.all())
        for widget in widgets:
            self.widgets[widget.pk] = widget

        return card

    def add_function(self, function):
        """
        Adds a FunctionXGraph record to this graph

        Arguments:
        node -- an object representing a FunctionXGraph instance or an actual models.CardModel instance

        """

        if not isinstance(function, models.FunctionXGraph):
            if isinstance(function, dict):
                functionobj = models.FunctionXGraph(**function.copy())
            else:
                functionobj = function.copy()
            function = models.FunctionXGraph()
            function.function_id = functionobj.function_id
            function.config = functionobj.config

        function.graph = self

        self._functions.append(function)

        return function

    def _compare(self, obj1, obj2, additional_excepted_keys=[]):
        excluded_keys = ["_state"] + additional_excepted_keys
        d1, d2 = obj1.__dict__, obj2.__dict__
        old, new = {}, {}
        for k, v in list(d1.items()):
            if k in excluded_keys:
                continue
            try:
                if v != d2[k]:
                    old.update({k: v})
                    new.update({k: d2[k]})
            except KeyError:
                old.update({k: v})
        return old, new

    def update_es_node_mapping(self, node, datatype_factory, se):
        already_saved = models.Node.objects.filter(pk=node.nodeid).exists()
        saved_node_datatype = None
        if already_saved:
            saved_node = models.Node.objects.get(pk=node.nodeid)
            saved_node_datatype = saved_node.datatype
        if saved_node_datatype != node.datatype:
            datatype = datatype_factory.get_instance(node.datatype)
            datatype_mapping = datatype.get_es_mapping(node.nodeid)
            if datatype_mapping and datatype_factory.datatypes[node.datatype].defaultwidget:
                se.create_mapping("resources", body=datatype_mapping)

    def save(self, validate=True, nodeid=None):
        """
        Saves an a graph and its nodes, edges, and nodegroups back to the db
        creates associated card objects if any of the nodegroups don't already have a card

        Arguments:
        validate -- True to validate the graph before saving, defaults to True

        """

        if validate:
            self.validate()

        with transaction.atomic():
            super(Graph, self).save()
            for nodegroup in self.get_nodegroups():
                nodegroup.save()

            se = SearchEngineFactory().create()
            datatype_factory = DataTypeFactory()

            if nodeid is not None:
                node = self.nodes[nodeid]
                self.update_es_node_mapping(node, datatype_factory, se)
                node.save()
            else:
                for node in self.nodes.values():
                    self.update_es_node_mapping(node, datatype_factory, se)
                    node.save()

            for edge in self.edges.values():
                edge.save()

            for card in self.cards.values():
                card.save()

            for constraint in self._card_constraints:
                constraint.save()

            for constraint_x_node in self._constraints_x_nodes:
                node_constraint = models.ConstraintXNode()
                node_constraint.node = models.Node.objects.get(pk=constraint_x_node["node"])
                node_constraint.constraint = constraint_x_node["constraint"]
                node_constraint.save()

            for widget in self.widgets.values():
                widget.save()

            for functionxgraph in self._functions:
                # Right now this only saves a functionxgraph record if the function is present in the database. Otherwise it silently fails.
                if functionxgraph.function_id in [str(id) for id in models.Function.objects.values_list("functionid", flat=True)]:
                    functionxgraph.save()

            for nodegroup in self._nodegroups_to_delete:
                nodegroup.delete()
            self._nodegroups_to_delete = []

        return self

    def delete(self):
        if self.is_editable() is True:
            with transaction.atomic():
                for nodegroup in self.get_nodegroups():
                    nodegroup.delete()

                for edge in self.edges.values():
                    edge.delete()

                for node in self.nodes.values():
                    node.delete()

                for card in self.cards.values():
                    card.delete()

                for widget in self.widgets.values():
                    widget.delete()

                super(Graph, self).delete()
        else:
            raise GraphValidationError(
                _(
                    "Your resource model: {0}, already has instances saved. You cannot delete a Resource Model with instances.".format(
                        self.name
                    )
                )
            )

    def delete_instances(self, verbose=False):
        """
        deletes all associated resource instances

        """
        if verbose is True:
            bar = pyprind.ProgBar(Resource.objects.filter(graph_id=self.graphid).count())
        for resource in Resource.objects.filter(graph_id=self.graphid):
            resource.delete()
            if verbose is True:
                bar.update()
        if verbose is True:
            print(bar)

    def get_tree(self, root=None):
        """
        returns a tree based representation of this graph

        Keyword Arguments:
        root -- the node from which to root the tree, defaults to the root node of this graph

        """

        tree = {"node": root if root else self.root, "children": [], "parent_edge": None}

        def find_child_edges(tree):
            for edge_id, edge in self.edges.items():
                if edge.domainnode == tree["node"]:
                    tree["children"].append(find_child_edges({"node": edge.rangenode, "children": [], "parent_edge": edge}))

            return tree

        return find_child_edges(tree)

    def populate_null_nodegroups(self):
        """
        populates any blank nodegroup ids of the nodes in this graph with the nearest parent node

        """

        tree = self.get_tree()

        def traverse_tree(tree, current_nodegroup=None):
            if tree["node"]:
                if tree["node"].is_collector:
                    nodegroup = self.get_or_create_nodegroup(nodegroupid=tree["node"].nodegroup_id)
                    nodegroup.parentnodegroup = current_nodegroup
                    current_nodegroup = nodegroup

                tree["node"].nodegroup = current_nodegroup

            for child in tree["children"]:
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
            branch_copy = branch_graph.copy()["copy"]
            branch_copy.root.istopnode = False

            newEdge = models.Edge(domainnode=nodeToAppendTo, rangenode=branch_copy.root, ontologyproperty=property, graph=self)
            branch_copy.add_edge(newEdge)

            for node in branch_copy.nodes.values():
                self.add_node(node)
            for card in branch_copy.get_cards():
                self.add_card(card)
            for edge in branch_copy.edges.values():
                self.add_edge(edge)
            for widget in branch_copy.widgets.values():
                self.widgets[widget.pk] = widget

            self.populate_null_nodegroups()
            sibling_node_names = [node.name for node in self.get_sibling_nodes(branch_copy.root)]
            branch_copy.root.name = self.make_name_unique(branch_copy.root.name, sibling_node_names)
            branch_copy.root.description = branch_graph.description

            if self.ontology is None:
                branch_copy.clear_ontology_references()

            return branch_copy

    def make_name_unique(self, name, names_to_check):
        """
        Makes a name unique among a list of name

        Arguments:
        name -- the name to check and modfiy to make unique in the list of "names_to_check"
        names_to_check -- a list of names that "name" should be unique among
        """

        i = 1
        temp_node_name = name
        while temp_node_name in names_to_check:
            temp_node_name = "{0}_{1}".format(name, i)
            i += 1
        return temp_node_name

    def append_node(self, nodeid=None):
        """
        Appends a single node onto this graph

        Keyword Arguments:
        nodeid -- if given will append the node to this node, if not supplied will
        append the node to the root of this graph

        """

        node_names = [node.name for node in self.nodes.values()]
        temp_node_name = self.make_name_unique(self.temp_node_name, node_names)
        nodeToAppendTo = self.nodes[uuid.UUID(str(nodeid))] if nodeid else self.root
        card = None

        if not settings.OVERRIDE_RESOURCE_MODEL_LOCK:
            tile_count = models.TileModel.objects.filter(nodegroup_id=nodeToAppendTo.nodegroup_id).count()
            if tile_count > 0:
                raise GraphValidationError(
                    _(
                        "Your resource model: {0}, already has instances saved. "
                        + "You cannot modify a Resource Model with instances.".format(self.name)
                    ),
                    1006,
                )

        nodegroup = None
        if nodeToAppendTo.nodeid == self.root.nodeid and self.isresource is True:
            newid = uuid.uuid1()
            nodegroup = models.NodeGroup.objects.create(pk=newid)
            card = models.CardModel.objects.create(nodegroup=nodegroup, name=temp_node_name, graph=self)
            newNode = models.Node(
                nodeid=newid, name=temp_node_name, istopnode=False, ontologyclass=None, datatype="semantic", nodegroup=nodegroup, graph=self
            )
        else:
            newNode = models.Node(
                nodeid=uuid.uuid1(), name=temp_node_name, istopnode=False, ontologyclass=None, datatype="semantic", graph=self
            )

        newEdge = models.Edge(domainnode=nodeToAppendTo, rangenode=newNode, ontologyproperty=None, graph=self)
        self.add_node(newNode)
        self.add_edge(newEdge)

        self.populate_null_nodegroups()

        # assign the first class and property found
        if self.ontology:
            ontology_classes = self.get_valid_ontology_classes(newNode.nodeid, nodeToAppendTo.nodeid)
            if len(ontology_classes) > 0:
                newEdge.ontologyproperty = ontology_classes[0]["ontology_property"]
                newNode.ontologyclass = ontology_classes[0]["ontology_classes"][0]
            else:
                raise GraphValidationError(_("Ontology rules don't allow this node to be appended"))
        return {"node": newNode, "edge": newEdge, "card": card, "nodegroup": nodegroup}

    def clear_ontology_references(self):
        """
        removes any references to ontology classes and properties in a graph

        """

        for node_id, node in self.nodes.items():
            node.ontologyclass = None

        for edge_id, edge in self.edges.items():
            edge.ontologyproperty = None

        self.ontology = None

    def replace_config_ids(self, config, maps=[]):
        """
        Replaces node, nodegroup, card, and formids in configuration json objects during
        graph cloning/copying
        """
        str_forms_config = json.dumps(config)
        for map in maps:
            for k, v in map.items():
                str_forms_config = str_forms_config.replace(str(k), str(v))
        return json.loads(str_forms_config)

    def copy_functions(self, other_graph, id_maps=[]):
        """
        Copies the graph_x_function relationships from a different graph and relates
        the same functions to this graph.

        """
        for function_x_graph in other_graph.functionxgraph_set.all():
            config_copy = self.replace_config_ids(function_x_graph.config, id_maps)
            function_copy = models.FunctionXGraph(function=function_x_graph.function, config=config_copy, graph=self)
            function_copy.save()

    def copy(self, root=None):
        """
        returns an unsaved copy of self

        """

        nodegroup_map = {}

        copy_of_self = deepcopy(self)

        if root is not None:
            root["nodegroup_id"] = root["nodeid"]
            root["istopnode"] = True
            updated_values = copy_of_self.update_node(root)
            root_node = updated_values["node"]
            root_card = updated_values["card"]
            tree = self.get_tree(root_node)

            def flatten_tree(tree, node_id_list=[]):
                node_id_list.append(tree["node"].pk)
                for node in tree["children"]:
                    flatten_tree(node, node_id_list)
                return node_id_list

            node_ids = flatten_tree(tree)
            copy_of_self.edges = {edge_id: edge for edge_id, edge in copy_of_self.edges.items() if edge.domainnode_id in node_ids}
            copy_of_self.nodes = {node_id: node for node_id, node in copy_of_self.nodes.items() if node_id in node_ids}
            copy_of_self.cards = {card_id: card for card_id, card in copy_of_self.cards.items() if card.nodegroup_id in node_ids}
            copy_of_self.widgets = {
                widget_id: widget for widget_id, widget in copy_of_self.widgets.items() if widget.card.nodegroup_id in node_ids
            }
            for widget_id, widget in copy_of_self.widgets.items():
                if widget.card.nodegroup_id not in node_ids:
                    widget.card = root_card
            copy_of_self.root = root_node
            copy_of_self.name = root_node.name
            copy_of_self.isresource = False
            copy_of_self.subtitle = ""
            copy_of_self.description = ""
            copy_of_self.author = ""

        # returns a list of node ids sorted by nodes that are collector nodes first and then others last
        node_ids = sorted(copy_of_self.nodes, key=lambda node_id: copy_of_self.nodes[node_id].is_collector, reverse=True)

        for nodeid, node in copy_of_self.nodes.items():
            if node.datatype == "geojson-feature-collection":
                node.config["advancedStyle"] = ""
                node.config["advancedStyling"] = False
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
                if old_nodegroup_id not in nodegroup_map:
                    nodegroup_map[old_nodegroup_id] = node.nodegroup_id
                for card in copy_of_self.cards.values():
                    if str(card.nodegroup_id) == str(old_nodegroup_id):
                        new_id = uuid.uuid1()
                        card_map[card.pk] = new_id
                        card.pk = new_id
                        card.nodegroup = node.nodegroup
                        card.graph = copy_of_self

            else:
                node.nodegroup = None

        for widget in copy_of_self.widgets.values():
            widget.pk = uuid.uuid1()
            widget.node_id = node_map[widget.node_id]
            widget.card_id = card_map[widget.card_id]

        copy_of_self.populate_null_nodegroups()

        copy_of_self.nodes = {node.pk: node for node_id, node in copy_of_self.nodes.items()}

        for edge_id, edge in copy_of_self.edges.items():
            edge.pk = uuid.uuid1()
            edge.graph = copy_of_self
            edge.domainnode_id = edge.domainnode.pk
            edge.rangenode_id = edge.rangenode.pk

        copy_of_self.edges = {edge.pk: edge for edge_id, edge in copy_of_self.edges.items()}

        return {"copy": copy_of_self, "cards": card_map, "nodes": node_map, "nodegroups": nodegroup_map}

    def move_node(self, nodeid, property, newparentnodeid, skip_validation=False):
        """
        move a node and it's children to a different location within this graph

        Arguments:
        nodeid -- the id of node being moved

        property -- the property value to conect the node to it's new parent nodegroup

        newparentnodeid -- the parent node id that the node is being moved to

        skip_validation -- don't validate the resultant graph (post move), defaults to False

        """

        ret = {"nodes": [], "edges": []}
        nodegroup = None
        node = self.nodes[uuid.UUID(str(nodeid))]

        graph_dict = self.serialize()
        graph_dict["nodes"] = []
        graph_dict["edges"] = []
        graph_dict["cards"] = []

        def traverse_tree(tree):
            graph_dict["nodes"].append(tree["node"])
            for child in tree["children"]:
                graph_dict["edges"].append({"domainnode_id": tree["node"]["nodeid"], "rangenode_id": child["node"]["nodeid"]})
                traverse_tree(child)

        tree = JSONSerializer().serializeToPython(self.get_tree(node))
        tree["node"]["istopnode"] = True
        traverse_tree(tree)

        if skip_validation or self.can_append(Graph(graph_dict), self.nodes[uuid.UUID(str(newparentnodeid))]):
            if not node.is_collector:
                nodegroup = node.nodegroup

                child_nodes, child_edges = node.get_child_nodes_and_edges()
                child_nodes.append(node)
                for child_node in child_nodes:
                    if child_node.nodegroup == nodegroup:
                        self.nodes[child_node.pk].nodegroup = None
                        ret["nodes"].append(child_node)

            for edge_id, edge in self.edges.items():
                if edge.rangenode == node:
                    edge.domainnode = self.nodes[uuid.UUID(str(newparentnodeid))]
                    ret["edges"].append(edge)

            self.populate_null_nodegroups()
            return ret

    def update_node(self, node):
        """
        updates a node in the graph

        Arguments:
        node -- a python dictionary representing a node object to be used to update the graph

        """
        node["nodeid"] = uuid.UUID(str(node.get("nodeid")))
        old_node = self.nodes.pop(node["nodeid"])
        new_node = self.add_node(node)
        new_card = None

        for edge_id, edge in self.edges.items():
            if edge.domainnode_id == new_node.nodeid:
                edge.domainnode = new_node
            if edge.rangenode_id == new_node.nodeid:
                edge.rangenode = new_node
                edge.ontologyproperty = node.get("parentproperty", None)

        if node["exportable"] is not None:
            new_node.exportable = node["exportable"]
        if node["fieldname"] is not None:
            new_node.fieldname = node["fieldname"]
        self.populate_null_nodegroups()

        # new_node will always have a nodegroup id even it if was set to None becuase populate_null_nodegroups
        # will populate the nodegroup id with the parent nodegroup
        # add/remove a card if a nodegroup was added/removed
        if new_node.nodegroup_id != old_node.nodegroup_id:
            if new_node.is_collector:
                # add a card
                new_card = models.CardModel(name=new_node.name, nodegroup=new_node.nodegroup)
                self.add_card(new_card)
            else:
                self._nodegroups_to_delete = [old_node.nodegroup]
                # remove a card
                self.cards = {card_id: card for card_id, card in self.cards.items() if card.nodegroup_id != old_node.nodegroup_id}

        try:
            new_card = models.CardModel.objects.get(name=old_node.name, nodegroup=new_node.nodegroup)
            for cardid, card in self.cards.items():
                if cardid == new_card.cardid:
                    card.name = new_node.name
        except ObjectDoesNotExist:
            pass

        return {"card": new_card, "node": new_node}

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
            tile_count = models.TileModel.objects.filter(nodegroup=node.nodegroup).count()
            if self.is_editable() is False and tile_count > 0:
                raise GraphValidationError(
                    _(
                        "Your resource model: {self.name}, already has instances saved. \
                            You cannot delete nodes from a Resource Model with instances."
                    ).format(**locals()),
                    1006,
                )

            def traverse_tree(tree):
                nodes.append(tree["node"])
                if tree["node"].is_collector:
                    nodegroups.append(tree["node"].nodegroup)
                for child in tree["children"]:
                    edges.append(child["parent_edge"])
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

        found = False
        if self.ontology is not None and graphToAppend.ontology is None:
            raise GraphValidationError(_("The graph you wish to append needs to define an ontology"))

        if self.ontology is not None and graphToAppend.ontology is not None:
            for domain_connection in graphToAppend.get_valid_domain_ontology_classes():
                for ontology_class in domain_connection["ontology_classes"]:
                    if ontology_class == nodeToAppendTo.ontologyclass:
                        found = True
                        break

                if found:
                    break

            if not found:
                raise GraphValidationError(_("Ontology rules don't allow this graph to be appended"))
        return True

    def get_parent_node(self, nodeid):
        """
        get the parent node of a node with the given nodeid

        Arguments:
        nodeid -- the node we want to find the parent of

        """

        if str(self.root.nodeid) == str(nodeid):
            return None

        for edge_id, edge in self.edges.items():
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
            ret.extend(self.get_child_nodes(edge.rangenode_id))
        return ret

    def get_sibling_nodes(self, node):
        """
        Given a node will get all of that nodes siblings excluding the given node itself

        """

        sibling_nodes = []
        if node.istopnode is False:
            incoming_edge = list(filter(lambda x: x.rangenode_id == node.nodeid, self.edges.values()))[0]
            parent_node_id = incoming_edge.domainnode_id
            sibling_nodes = [
                edge.rangenode
                for edge in filter(lambda x: x.domainnode_id == parent_node_id, self.edges.values())
                if edge.rangenode.nodeid != node.nodeid
            ]
        return sibling_nodes

    def get_out_edges(self, nodeid):
        """
        get all the edges of a node with the given nodeid where that node is the domainnode

        Arguments:
        nodeid -- the nodeid of the node we want to find the edges of

        """

        ret = []
        for edge_id, edge in self.edges.items():
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

        for node in self.get_parent_nodes_and_edges(node)["nodes"]:
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
        for edge in self.edges.values():
            if edge.rangenode_id == node.nodeid:
                edges.append(edge)
                nodes.append(edge.domainnode)

                nodesAndEdges = self.get_parent_nodes_and_edges(edge.domainnode)
                nodes.extend(nodesAndEdges["nodes"])
                edges.extend(nodesAndEdges["edges"])

        return {"nodes": nodes, "edges": edges}

    def is_group_semantic(self, node):
        """
        test to see if all the nodes in a group are semantic

        returns true if the group contains only semantic nodes, otherwise false

        Arguments:
        node -- the node to use as a basis of finding the group

        """

        for node in self.get_grouped_nodes(node):
            if node.datatype != "semantic":
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
        nodegroup_id = node.nodegroup_id
        if nodegroup_id == "":
            return [node]

        for node in self.nodes.values():
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
            return ontology_classes.target["up"]
        else:
            return []

    def get_valid_ontology_classes(self, nodeid=None, parent_nodeid=None):
        """
        get possible ontology properties (and related classes) a node with the given nodeid can have
        taking into consideration its current position in the graph

        Arguments:
        nodeid -- the id of the node in question

        """

        ret = []
        if nodeid and self.ontology_id is not None:
            if parent_nodeid is None:
                parent_node = self.get_parent_node(nodeid)
            else:
                parent_node = models.Node.objects.get(pk=parent_nodeid)
            out_edges = self.get_out_edges(nodeid)

            ontology_classes = set()
            if len(out_edges) > 0:
                for edge in out_edges:
                    for ontology_property in models.OntologyClass.objects.get(
                        source=edge.rangenode.ontologyclass, ontology_id=self.ontology_id
                    ).target["up"]:
                        if edge.ontologyproperty == ontology_property["ontology_property"]:
                            if len(ontology_classes) == 0:
                                ontology_classes = set(ontology_property["ontology_classes"])
                            else:
                                ontology_classes = ontology_classes.intersection(set(ontology_property["ontology_classes"]))

                            if len(ontology_classes) == 0:
                                break

            # get a list of properties (and corresponding classes) that could be used to relate to my parent node
            # limit the list of properties based on the intersection between the property's classes and the list of
            # ontology classes we found above
            if parent_node:
                range_ontologies = models.OntologyClass.objects.get(source=parent_node.ontologyclass, ontology_id=self.ontology_id).target[
                    "down"
                ]
                if len(out_edges) == 0:
                    return range_ontologies
                else:
                    for ontology_property in range_ontologies:
                        ontology_property["ontology_classes"] = list(
                            set(ontology_property["ontology_classes"]).intersection(ontology_classes)
                        )

                        if len(ontology_property["ontology_classes"]) > 0:
                            ret.append(ontology_property)

            else:
                # if a brand new resource
                if len(out_edges) == 0:
                    ret = [
                        {
                            "ontology_property": "",
                            "ontology_classes": models.OntologyClass.objects.values_list("source", flat=True).filter(
                                ontology_id=self.ontology_id
                            ),
                        }
                    ]
                else:
                    # if no parent node then just use the list of ontology classes from above, there will be no properties to return
                    ret = [{"ontology_property": "", "ontology_classes": list(ontology_classes)}]
        return ret

    def get_nodegroups(self, nodegroupid=None):
        """
        get the nodegroups associated with this graph

        """

        nodegroups = set()
        for node in self.nodes.values():
            if node.is_collector:
                nodegroups.add(node.nodegroup)
        for card in self.cards.values():
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

        for card in self.cards.values():
            if card.nodegroup.parentnodegroup is None:
                return card

    def get_cards(self, check_if_editable=True):
        """
        get the card data (if any) associated with this graph

        """

        cards = []
        for card in self.cards.values():
            is_editable = True
            if self.isresource:
                if not card.name:
                    card.name = self.nodes[card.nodegroup_id].name
                if not card.description:
                    try:
                        card.description = self.nodes[card.nodegroup_id].description
                    except KeyError as e:
                        print("Error: card.description not accessible, nodegroup_id not in self.nodes: ", e)
                if check_if_editable:
                    is_editable = card.is_editable()
            else:
                if card.nodegroup.parentnodegroup_id is None:
                    card.name = self.name
                    card.description = self.description
                else:
                    if not card.name:
                        card.name = self.nodes[card.nodegroup_id].name
                    if not card.description:
                        card.description = self.nodes[card.nodegroup_id].description
            card_dict = JSONSerializer().serializeToPython(card)
            card_dict["is_editable"] = is_editable
            card_constraints = card.constraintmodel_set.all()
            card_dict["constraints"] = JSONSerializer().serializeToPython(card_constraints)
            cards.append(card_dict)

        return cards

    def get_widgets(self):
        """
        get the widget data (if any) associated with this graph

        """
        widgets = []
        for widget in self.widgets.values():
            widget_dict = JSONSerializer().serializeToPython(widget)
            widgets.append(widget_dict)

        return widgets

    def serialize(self, fields=None, exclude=None):
        """
        serialize to a different form then used by the internal class structure

        used to append additional values (like parent ontology properties) that
        internal objects (like models.Nodes) don't support

        """
        exclude = [] if exclude is None else exclude

        ret = JSONSerializer().handle_model(self, fields, exclude)
        ret["root"] = self.root

        if "relatable_resource_model_ids" not in exclude:
            ret["relatable_resource_model_ids"] = [str(relatable_node.graph_id) for relatable_node in self.root.get_relatable_resources()]
        else:
            ret.pop("relatable_resource_model_ids", None)

        check_if_editable = "is_editable" not in exclude
        ret["is_editable"] = self.is_editable() if check_if_editable else ret.pop("is_editable", None)
        ret["cards"] = self.get_cards(check_if_editable=check_if_editable) if "cards" not in exclude else ret.pop("cards", None)

        if "widgets" not in exclude:
            ret["widgets"] = self.get_widgets()
        ret["nodegroups"] = self.get_nodegroups() if "nodegroups" not in exclude else ret.pop("nodegroups", None)
        ret["domain_connections"] = (
            self.get_valid_domain_ontology_classes() if "domain_connections" not in exclude else ret.pop("domain_connections", None)
        )
        ret["is_editable"] = self.is_editable() if "is_editable" not in exclude else ret.pop("is_editable", None)
        ret["functions"] = (
            models.FunctionXGraph.objects.filter(graph_id=self.graphid) if "functions" not in exclude else ret.pop("functions", None)
        )

        parentproperties = {self.root.nodeid: ""}

        for edge_id, edge in self.edges.items():
            parentproperties[edge.rangenode_id] = edge.ontologyproperty

        ret["edges"] = [edge for key, edge in self.edges.items()] if "edges" not in exclude else ret.pop("edges", None)

        if "nodes" not in exclude:
            ret["nodes"] = []
            for key, node in self.nodes.items():
                nodeobj = JSONSerializer().serializeToPython(node)
                nodeobj["parentproperty"] = parentproperties[node.nodeid]
                ret["nodes"].append(nodeobj)
        else:
            ret.pop("nodes", None)

        res = JSONSerializer().serializeToPython(ret)

        return res

    def check_if_resource_is_editable(self):
        def find_unpermitted_edits(obj_a, obj_b, ignore_list, obj_type):
            # if node_tile_count > 0:
            res = None
            pre_diff = self._compare(obj_a, obj_b, ignore_list)
            diff = [x for x in pre_diff if len(list(x.keys())) > 0]
            if len(diff) > 0:
                if obj_type == "node":
                    tile_count = models.TileModel.objects.filter(nodegroup_id=db_node.nodegroup_id).count()
                    res = diff if tile_count > 0 else None  # If your node has no data, you can change any property
            return res

        if self.isresource is True:
            if self.is_editable() is False:
                unpermitted_edits = []
                db_nodes = models.Node.objects.filter(graph=self)
                for db_node in db_nodes:
                    unpermitted_node_edits = find_unpermitted_edits(
                        db_node,
                        self.nodes[db_node.nodeid],
                        ["name", "issearchable", "ontologyclass", "description", "isrequired", "fieldname", "exportable"],
                        "node",
                    )
                    if unpermitted_node_edits is not None:
                        unpermitted_edits.append(unpermitted_node_edits)
                db_graph = Graph.objects.get(pk=self.graphid)
                unpermitted_graph_edits = find_unpermitted_edits(
                    db_graph,
                    self,
                    [
                        "name",
                        "ontology_id",
                        "subtitle",
                        "iconclass",
                        "author",
                        "description",
                        "isactive",
                        "color",
                        "nodes",
                        "edges",
                        "cards",
                        "nodegroup_id",
                    ],
                    "graph",
                )
                if unpermitted_graph_edits is not None:
                    unpermitted_edits.append(unpermitted_graph_edits)
                if len(unpermitted_edits) > 0:
                    raise GraphValidationError(
                        _(
                            "Your resource model: {self.name}, already has instances saved. \
                                You cannot modify a Resource Model with instances."
                        ).format(**locals()),
                        1006,
                    )

    def _validate_node_name(self, node):
        """
        Verifies a node's name is unique to its nodegroup
        Prevents a user from changing the name of a node that already has tiles.
        Verifies a node's name is unique to its sibling nodes.
        """

        if node.istopnode:
            return
        else:
            names_in_nodegroup = [v.name for k, v in self.nodes.items() if v.nodegroup_id == node.nodegroup_id]
            unique_names_in_nodegroup = {n for n in names_in_nodegroup}
            if len(names_in_nodegroup) > len(unique_names_in_nodegroup):
                message = _('Duplicate node name: "{0}". All node names in a card must be unique.'.format(node.name))
                raise GraphValidationError(message)
            elif node.is_editable() is False:
                if node.name != models.Node.objects.values_list("name", flat=True).get(pk=node.nodeid):
                    message = "The name of this node cannot be changed because business data has already been saved to a card that this node is part of."
                    raise GraphValidationError(_(message))
            else:
                sibling_node_names = [node.name for node in self.get_sibling_nodes(node)]
                if node.name in sibling_node_names:
                    message = _('Duplicate node name: "{0}". All sibling node names must be unique.'.format(node.name))
                    raise GraphValidationError(message)

    def validate(self):
        """
        validates certain aspects of resource graphs according to defined rules:
            - The root node of a "Resource" can only be a semantic node, and must be a collector
            - A node group that has child node groups may not itself be a child node group
            - A node group can only have child node groups if the node group only contains semantic nodes
            - If graph has an ontology, nodes must have classes and edges must have properties that are ontologically valid
            - If the graph has no ontology, nodes and edges should have null values for ontology class and property respectively

        """
        # validates that the resource graph is editable despite having saved instances.
        self.check_if_resource_is_editable()

        # validates that the top node of a resource graph is semantic and a collector
        if self.isresource is True:
            if self.root.is_collector is True:
                raise GraphValidationError(
                    _(
                        "The top node of your resource graph: {self.root.name} needs to be a collector. \
                            Hint: check that nodegroup_id of your resource node(s) are not null."
                    ).format(**locals()),
                    997,
                )
            if self.root.datatype != "semantic":
                raise GraphValidationError(_("The top node of your resource graph must have a datatype of 'semantic'."), 998)
        else:
            if self.root.is_collector is False:
                if len(self.nodes) > 1:
                    raise GraphValidationError(
                        _("If your graph contains more than one node and is not a resource the root must be a collector."), 999
                    )

        def validate_fieldname(fieldname, fieldnames):
            if node.fieldname == "":
                raise GraphValidationError(_("Field name must not be blank."), 1008)
            if fieldname.replace("_", "").isalnum() is False:
                raise GraphValidationError(_("Field name must contain only alpha-numeric characters or underscores."), 1010)
            if fieldname[0] == "_" or fieldname[0].isdigit():
                raise GraphValidationError(_("Field name cannot begin with an underscore or number"), 1011)
            if len(fieldname) > 10:
                fieldname = fieldname[:10]
            try:
                dupe = fieldnames[fieldname]
                raise GraphValidationError(
                    _("Field name must be unique to the graph; '{fieldname}' already exists.").format(**locals()), 1009
                )
            except KeyError:
                fieldnames[fieldname] = True

            return fieldname

        fieldnames = {}
        for node_id, node in self.nodes.items():
            self._validate_node_name(node)
            if node.exportable is True:
                if node.fieldname is not None:
                    validated_fieldname = validate_fieldname(node.fieldname, fieldnames)
                    if validated_fieldname != node.fieldname:
                        node.fieldname = validated_fieldname

        # validate that nodes in a resource graph belong to the ontology assigned to the resource graph
        if self.ontology is not None:
            ontology_classes = self.ontology.ontologyclasses.values_list("source", flat=True)

            for node_id, node in self.nodes.items():
                if node.ontologyclass == "":
                    raise GraphValidationError(_("A valid {0} ontology class must be selected").format(self.ontology.name), 1000)
                if node.ontologyclass not in ontology_classes:
                    raise GraphValidationError(
                        _("'{0}' is not a valid {1} ontology class").format(node.ontologyclass, self.ontology.name), 1001
                    )

            for edge_id, edge in self.edges.items():
                # print 'checking %s-%s-%s' % (edge.domainnode.ontologyclass,edge.ontologyproperty, edge.rangenode.ontologyclass)
                if edge.ontologyproperty is None:
                    raise GraphValidationError(
                        _(
                            "You must specify an ontology property. Your graph isn't semantically valid. \
                                Entity domain '{edge.domainnode.ontologyclass}' and \
                                Entity range '{edge.rangenode.ontologyclass}' can not be related via Property '{edge.ontologyproperty}'."
                        ).format(**locals()),
                        1002,
                    )
                property_found = False
                okay = False
                ontology_classes = self.ontology.ontologyclasses.get(source=edge.domainnode.ontologyclass)
                for classes in ontology_classes.target["down"]:
                    if classes["ontology_property"] == edge.ontologyproperty:
                        property_found = True
                        if edge.rangenode.ontologyclass in classes["ontology_classes"]:
                            okay = True
                            break

                if not okay:
                    raise GraphValidationError(
                        _(
                            "Your graph isn't semantically valid. Entity domain '{edge.domainnode.ontologyclass}' and \
                                Entity range '{edge.rangenode.ontologyclass}' cannot \
                                be related via Property '{edge.ontologyproperty}'."
                        ).format(**locals()),
                        1003,
                    )
                elif not property_found:
                    raise GraphValidationError(
                        _("'{0}' is not found in the {1} ontology or is not a valid ontology property for Entity domain '{2}'.").format(
                            edge.ontologyproperty, self.ontology.name, edge.domainnode.ontologyclass
                        ),
                        1004,
                    )
        else:
            for node_id, node in self.nodes.items():
                if node.ontologyclass is not None:
                    raise GraphValidationError(
                        _("You have assigned ontology classes to your graph nodes but not assigned an ontology to your graph."), 1005
                    )

        # make sure the supplied json-ld context is valid
        # https://www.w3.org/TR/json-ld/#the-context
        context = self.jsonldcontext
        try:
            if context is None:
                context = {"@context": {}}
            else:
                context = JSONDeserializer().deserialize(context)
        except ValueError:
            if context == "":
                context = {}
            context = {"@context": context}
        except AttributeError:
            context = {"@context": {}}

        try:
            out = compact({}, context)
        except JsonLdError:
            raise GraphValidationError(_("The json-ld context you supplied wasn't formatted correctly."), 1006)

        if self.slug is not None:
            graphs_with_matching_slug = models.GraphModel.objects.exclude(slug__isnull=True).filter(slug=self.slug)
            if graphs_with_matching_slug.exists() and graphs_with_matching_slug[0].graphid != self.graphid:
                raise GraphValidationError(_("Another resource modal already uses the slug '{self.slug}'").format(**locals()), 1007)


class GraphValidationError(Exception):
    def __init__(self, message, code=None):
        self.title = _("Graph Validation Error")
        self.message = message
        self.code = code

    def __str__(self):
        return repr(self.message)
