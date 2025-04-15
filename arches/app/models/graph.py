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
import uuid
from copy import deepcopy
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, connection
from django.db.utils import IntegrityError
from arches.app.const import IntegrityCheck
from arches.app.models import models
from arches.app.models.card import Card
from arches.app.models.querysets.graph import GraphQuerySet
from arches.app.models.system_settings import settings
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.etl_modules.bulk_data_deletion import BulkDataDeletion
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.utils.i18n import LanguageSynchronizer
from django.utils.translation import gettext as _
from pyld.jsonld import compact, JsonLdError
from django.db.models.base import Deferred
from django.utils import translation
from guardian.models import GroupObjectPermission, UserObjectPermission


logger = logging.getLogger(__name__)


class Graph(models.GraphModel):
    """
    Used for mapping complete resource graph objects to and from the database

    """

    objects = GraphQuerySet.as_manager()

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
                    if key not in (
                        "root",
                        "nodes",
                        "edges",
                        "cards",
                        "functions",
                        "is_editable",
                        "publication",
                        "user_permissions",
                        "group_permissions",
                        "resource_instance_lifecycle",
                    ):
                        setattr(self, key, value)

                try:
                    self.update_permissions_from_serialized_graph(args[0])
                except (
                    AttributeError
                ):  # AttributeError happens if attempting to update permissions on a non-existent NodeGroup
                    pass

                nodegroups = dict(
                    (item["nodegroupid"], item) for item in args[0]["nodegroups"]
                )
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
                        default_config = models.Function.objects.get(
                            functionid=function["function_id"]
                        ).defaultconfig
                        function["config"] = check_default_configs(
                            default_config, function_x_graph_config
                        )

                        self.add_function(function)

                self.populate_null_nodegroups()

                if "publication" in args[0] and args[0]["publication"] is not None:
                    publication_data = args[0]["publication"]
                    self.publication = models.GraphXPublishedGraph(**publication_data)

                if (
                    "resource_instance_lifecycle" in args[0]
                    and args[0]["resource_instance_lifecycle"] is not None
                ):
                    self.add_resource_instance_lifecycle(
                        args[0]["resource_instance_lifecycle"]
                    )
            else:
                self.cards = {card.pk: card for card in super().get_cards()}

                self.nodes = {node.pk: node for node in super().get_nodes()}
                for node in self.nodes.values():
                    if node.istopnode:
                        self.root = node

                self.edges = {edge.pk: edge for edge in super().get_edges()}
                # This resolves a tricky pointer issue with `append_branch`
                # and possibly other functions as well. This block should
                # be deleted when possible.
                for edge in self.edges.values():
                    edge.domainnode = self.nodes[edge.domainnode_id]
                    edge.rangenode = self.nodes[edge.rangenode_id]

                self.widgets = {
                    card_x_node_x_widget.pk: card_x_node_x_widget
                    for card_x_node_x_widget in super().get_card_x_node_x_widgets()
                }

    def refresh_from_database(self):
        """
        Updates card, edge, and node data from the database, bypassing the
        cached version of the graph
        """
        self.refresh_from_db()

        self.nodes = {}
        self.edges = {}
        self.cards = {}

        nodes = self.node_set.all()
        edges = self.edge_set.all()
        cards = self.cardmodel_set.all()

        edge_lookup = {
            edge["edgeid"]: edge
            for edge in json.loads(JSONSerializer().serialize(edges))
        }

        for card in cards:
            widgets = list(card.cardxnodexwidget_set.all())
            for widget in widgets:
                self.widgets[widget.pk] = widget

        node_lookup = {}
        for node in nodes:
            self.add_node(node)
            node_lookup[str(node.nodeid)] = node

        for edge in edges:
            edge_dict = edge_lookup[str(edge.edgeid)]
            edge.domainnode = node_lookup[edge_dict["domainnode_id"]]
            edge.rangenode = node_lookup[edge_dict["rangenode_id"]]
            self.add_edge(edge)

        for card in cards:
            self.add_card(card)

        self.populate_null_nodegroups()

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
            node.source_identifier_id = nodeobj.get("source_identifier_id", None)
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
            node.sortorder = nodeobj.get("sortorder", 0)
            node.fieldname = nodeobj.get("fieldname", "")
            node.hascustomalias = nodeobj.get("hascustomalias", False)
            node.sourcebranchpublication_id = nodeobj.get(
                "sourcebranchpublication_id", None
            )
            node.is_immutable = nodeobj.get("is_immutable", False)
            if node.hascustomalias or nodeobj.get("alias", False) is not False:
                node.alias = nodeobj.get("alias", "")
            else:
                self.create_node_alias(node)

            node.nodeid = uuid.UUID(str(node.nodeid))

            if node.nodegroup_id is not None and node.nodegroup_id != "":
                node.nodegroup_id = uuid.UUID(str(node.nodegroup_id))
                node.nodegroup = self.get_or_create_nodegroup(
                    nodegroupid=node.nodegroup_id
                )
                if nodegroups is not None and str(node.nodegroup_id) in nodegroups:
                    node.nodegroup.cardinality = nodegroups[str(node.nodegroup_id)][
                        "cardinality"
                    ]
                    node.nodegroup.legacygroupid = nodegroups[str(node.nodegroup_id)][
                        "legacygroupid"
                    ]
                    node.nodegroup.parentnodegroupid = nodegroups[
                        str(node.nodegroup_id)
                    ]["parentnodegroup_id"]
            else:
                node.nodegroup = None

        node.graph = self

        if self.ontology_id is None:
            node.ontologyclass = None
        if node.pk is None:
            node.pk = uuid.uuid1()
        if isinstance(node.pk, str):
            node.pk = uuid.UUID(node.pk)
        if node.istopnode:
            self.root = node

        self.nodes[node.pk] = node
        self.has_unpublished_changes = True

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

        self.has_unpublished_changes = True

        return edge

    def add_card_contraint(self, constraint, card):
        constraint_model = models.ConstraintModel()
        constraint_model.constraintid = constraint.get("constraintid", None)
        constraint_model.uniquetoallinstances = constraint.get(
            "uniquetoallinstances", False
        )
        constraint_model.card = card
        self._card_constraints.append(constraint_model)
        for nodeid in constraint.get("nodes", []):
            constraint_x_node = {"constraint": constraint_model, "node": nodeid}
            self._constraints_x_nodes.append(constraint_x_node)

        self.has_unpublished_changes = True

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
            card.component_id = cardobj.get(
                "component_id", uuid.UUID("f05e4d3a-53c1-11e8-b0ea-784f435179ea")
            )
            card.nodegroup_id = uuid.UUID(str(cardobj.get("nodegroup_id", "")))
            card.nodegroup = self.get_or_create_nodegroup(nodegroupid=card.nodegroup_id)
            card.config = cardobj.get("config", None)
            constraints = cardobj.get("constraints", "")
            constraints_with_nodes = [c for c in constraints if len(c["nodes"])]
            for constraint in constraints_with_nodes:
                self.add_card_contraint(constraint, card)

        card.graph = self

        if card.pk is None:
            card.pk = uuid.uuid1()

        self.cards[card.pk] = card
        self.has_unpublished_changes = True

        return card

    def add_function(self, function):
        """
        Adds a FunctionXGraph record to this graph

        Arguments:
        function -- an object representing a FunctionXGraph instance or an actual FunctionXGraph instance

        """

        if not isinstance(function, models.FunctionXGraph):
            function = models.FunctionXGraph(**function.copy())

        function.graph = self

        self._functions.append(function)
        self.has_unpublished_changes = True

        return function

    def add_resource_instance_lifecycle(self, resource_instance_lifecycle):
        """
        Adds a ResourceInstanceLifecycle to this graph

        Arguments:
        resource_instance_lifecycle -- a dictionary representing a models.ResourceInstanceLifecycle instance

        """

        resource_instance_lifecycle_query = (
            models.ResourceInstanceLifecycle.objects.filter(
                pk=resource_instance_lifecycle["id"]
            )
        )

        self.resource_instance_lifecycle = resource_instance_lifecycle_query.first()

        if not self.resource_instance_lifecycle:
            self.resource_instance_lifecycle = models.ResourceInstanceLifecycle(
                id=resource_instance_lifecycle["id"],
                name=resource_instance_lifecycle["name"],
            )

            resource_instance_lifecycle_states = []
            for resource_instance_lifecycle_state_json in resource_instance_lifecycle[
                "resource_instance_lifecycle_states"
            ]:
                next_resource_instance_lifecycle_states = (
                    resource_instance_lifecycle_state_json.pop(
                        "next_resource_instance_lifecycle_states"
                    )
                )
                previous_resource_instance_lifecycle_states = (
                    resource_instance_lifecycle_state_json.pop(
                        "previous_resource_instance_lifecycle_states"
                    )
                )

                resource_instance_lifecycle_state = (
                    models.ResourceInstanceLifecycleState(
                        **resource_instance_lifecycle_state_json
                    )
                )

                resource_instance_lifecycle_state.next_resource_instance_lifecycle_states.set(
                    next_resource_instance_lifecycle_states
                )
                resource_instance_lifecycle_state.previous_resource_instance_lifecycle_states.set(
                    previous_resource_instance_lifecycle_states
                )

                resource_instance_lifecycle_states.append(
                    resource_instance_lifecycle_state
                )

            self.resource_instance_lifecycle.resource_instance_lifecycle_states.set(
                resource_instance_lifecycle_states, bulk=False
            )

        self.has_unpublished_changes = True

        return self.resource_instance_lifecycle

    def update_es_node_mapping(self, node, datatype_factory, se):
        if self.isresource:
            already_saved = models.Node.objects.filter(pk=node.nodeid).exists()
            saved_node_datatype = None
            if already_saved:
                saved_node = models.Node.objects.get(pk=node.nodeid)
                saved_node_datatype = saved_node.datatype
            if saved_node_datatype != node.datatype:
                datatype = datatype_factory.get_instance(node.datatype)
                datatype_mapping = datatype.get_es_mapping(node.nodeid)
                if (
                    datatype_mapping
                    and datatype_factory.datatypes[node.datatype].defaultwidget
                ):
                    se.create_mapping("resources", body=datatype_mapping)

    def save(self, validate=True, nodeid=None):
        """
        Saves a graph and its nodes, edges, and nodegroups back to the db
        creates associated card objects if any of the nodegroups don't already have a card

        Arguments:
        validate -- True to validate the graph before saving, defaults to True

        """
        if validate:
            self.validate()

        with transaction.atomic():
            super(Graph, self).save()

            has_unpublished_changes = self.has_unpublished_changes

            for nodegroup in self.get_nodegroups():
                nodegroup.save()

            se = SearchEngineFactory().create()
            datatype_factory = DataTypeFactory()

            if nodeid is not None:
                node = self.nodes[nodeid]
                branch_publication_id = node.sourcebranchpublication_id
                self.update_es_node_mapping(node, datatype_factory, se)
                self.create_node_alias(node)
                try:
                    node.save()
                except ValueError as ve:
                    raise GraphValidationError(ve.args[0])
                except IntegrityError as err:
                    if "unique_alias_graph" in str(err):
                        message = _(
                            'Duplicate node alias: "{0}". All aliases must be unique in a resource model.'.format(
                                node.alias
                            )
                        )
                        raise GraphValidationError(message)
                    else:
                        logger.error(err)
                        message = _('Fail to save node "{0}".'.format(node.name))
                        raise GraphValidationError(message)
                if branch_publication_id:
                    for branch_node in models.Node.objects.filter(
                        sourcebranchpublication_id=branch_publication_id,
                        graph=node.graph,
                    ):
                        branch_node.save()

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
                node_constraint.node = models.Node.objects.get(
                    pk=constraint_x_node["node"]
                )
                node_constraint.constraint = constraint_x_node["constraint"]
                node_constraint.save()

            if self.widgets:
                for widget in self.widgets.values():
                    widget.save()

            for functionxgraph in self._functions:
                # Right now this only saves a functionxgraph record if the function is present in the database. Otherwise it silently fails.
                if functionxgraph.function_id in [
                    str(id)
                    for id in models.Function.objects.values_list(
                        "functionid", flat=True
                    )
                ]:

                    previous_functionxgraph_list = models.FunctionXGraph.objects.filter(
                        function_id=functionxgraph.function_id, graph_id=self.pk
                    )
                    if len(previous_functionxgraph_list):
                        previous_functionxgraph = previous_functionxgraph_list[0]
                        previous_functionxgraph.delete()

                try:
                    functionxgraph.save()
                except:
                    pass

            # edge case for instantiating a serialized_graph that has a publication
            if self.publication and not len(
                models.GraphXPublishedGraph.objects.filter(
                    publicationid=self.publication_id
                )
            ):
                self.publication.save()

                for language_tuple in settings.LANGUAGES:
                    language = models.Language.objects.get(code=language_tuple[0])

                    translation.activate(language=language_tuple[0])

                    models.PublishedGraph.objects.create(
                        publication=self.publication,
                        serialized_graph=JSONDeserializer().deserialize(
                            JSONSerializer().serialize(self, force_recalculation=True)
                        ),
                        language=language,
                    )

            # edge case for instantiating a serialized_graph that has a resource_instance_lifecycle not already in the system
            if self.resource_instance_lifecycle and not len(
                models.ResourceInstanceLifecycle.objects.filter(
                    pk=self.resource_instance_lifecycle.pk
                )
            ):
                for (
                    resource_instance_lifecycle_state
                ) in (
                    self.resource_instance_lifecycle.resource_instance_lifecycle_states.all()
                ):
                    resource_instance_lifecycle_state.save()

                self.resource_instance_lifecycle.save()

            for nodegroup in self._nodegroups_to_delete:
                nodegroup.delete()
            self._nodegroups_to_delete = []

            # becuase of signals listeners on related graph entities,
            # `has_unpublished_changes` must be updated manually after
            # all related entities have updated.
            self.has_unpublished_changes = has_unpublished_changes
            super().save()

        return self

    def delete(self):
        self.delete_associated_entities()
        super(Graph, self).delete()

        return self

    def delete_associated_entities(self):
        """
        Deletes all associated cards, cards_x_nodes_x_widgets, edges, nodes, and nodegroups
        """
        with transaction.atomic():
            try:
                draft_graph = Graph.objects.get(source_identifier_id=self.graphid)
                draft_graph.delete()
            except Graph.DoesNotExist:
                pass  # no draft_graph to delete

            for nodegroup in self.get_nodegroups(force_recalculation=True):
                nodegroup.delete()

            for edge in self.edges.values():
                edge.delete()

            for node in self.nodes.values():
                node.delete()

            for card in self.cards.values():
                card.delete()

            for widget in self.widgets.values():
                widget.delete()

        self.has_unpublished_changes = True

        return self

    def delete_instances(self, userid=None, verbose=False):
        """
        deletes all associated resource instances

        """

        bulk_deleter = BulkDataDeletion()
        loadid = uuid.uuid4()
        resp = bulk_deleter.delete_resources(
            userid, loadid, graphid=self.graphid, verbose=verbose
        )
        bulk_deleter.index_resource_deletion(loadid)

        return resp

    def get_tree(self, root=None):
        """
        returns a tree based representation of this graph

        Keyword Arguments:
        root -- the node from which to root the tree, defaults to the root node of this graph

        """

        tree = {
            "node": root if root else self.root,
            "children": [],
            "parent_edge": None,
        }

        def find_child_edges(tree):
            for edge_id, edge in self.edges.items():
                if edge.domainnode == tree["node"]:
                    tree["children"].append(
                        find_child_edges(
                            {
                                "node": edge.rangenode,
                                "children": [],
                                "parent_edge": edge,
                            }
                        )
                    )

            return tree

        return find_child_edges(tree)

    def populate_null_nodegroups(self):
        """
        populates any blank nodegroup ids of the nodes in this graph with the nearest parent node

        """

        tree = self.get_tree()
        nodegroups = self.get_nodegroups()

        def traverse_tree(tree, current_nodegroup=None):
            if tree["node"]:
                if tree["node"].is_collector:
                    nodegroup = self.get_or_create_nodegroup(
                        nodegroupid=tree["node"].nodegroup_id,
                        nodegroups_list=nodegroups,
                    )
                    nodegroup.parentnodegroup = current_nodegroup
                    current_nodegroup = nodegroup

                tree["node"].nodegroup = current_nodegroup

            for child in tree["children"]:
                traverse_tree(child, current_nodegroup)
            return tree

        traverse_tree(tree)

        self.has_unpublished_changes = True
        return tree

    def append_branch(
        self,
        property,
        nodeid=None,
        graphid=None,
        skip_validation=False,
        return_appended_graph=False,
    ):
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

        branch_graph = Graph.objects.get(pk=graphid)
        nodeToAppendTo = self.nodes[uuid.UUID(str(nodeid))] if nodeid else self.root

        if skip_validation or self.can_append(branch_graph, nodeToAppendTo):
            branch_copy = branch_graph.copy()["copy"]
            branch_publication_id = (
                branch_graph.publication_id
            )  # == branch_copy.publication_id
            branch_copy.root.istopnode = False

            newEdge = models.Edge(
                domainnode=nodeToAppendTo,
                rangenode=branch_copy.root,
                ontologyproperty=property,
                graph=self,
            )
            branch_copy.add_edge(newEdge)

            aliases = [node.alias for node in self.nodes.values()]
            branch_aliases = [node.alias for node in branch_copy.nodes.values()]

            for node in branch_copy.nodes.values():
                node.sourcebranchpublication_id = branch_publication_id

                if node.alias and node.alias in aliases:
                    node.alias = self.make_name_unique(
                        node.alias, aliases + branch_aliases, "_n"
                    )

                self.add_node(node)
            for card in branch_copy.get_cards():
                self.add_card(card)
            for edge in branch_copy.edges.values():
                self.add_edge(edge)
            for widget in branch_copy.widgets.values():
                self.widgets[widget.pk] = widget

            self.populate_null_nodegroups()
            sibling_node_names = [
                node.name for node in self.get_sibling_nodes(branch_copy.root)
            ]
            branch_copy.root.name = self.make_name_unique(
                branch_copy.root.name, sibling_node_names
            )
            branch_copy.root.description = branch_graph.description

            if self.ontology is None:
                branch_copy.clear_ontology_references()

            self.has_unpublished_changes = True

            if return_appended_graph:
                return self
            else:
                return branch_copy

    def make_name_unique(self, name, names_to_check, suffix_delimiter="_"):
        """
        Makes a name unique among a list of names

        Arguments:
        name -- the name to check and modfiy to make unique in the list of "names_to_check"
        names_to_check -- a list of names that "name" should be unique among
        """

        i = 1
        temp_node_name = name
        while temp_node_name in names_to_check:
            temp_node_name = "{0}{1}{2}".format(name, suffix_delimiter, i)
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
        nodegroup = None

        if nodeToAppendTo.nodeid == self.root.nodeid and self.isresource is True:
            newid = uuid.uuid1()
            nodegroup = models.NodeGroup.objects.create(pk=newid)
            card = models.CardModel.objects.create(
                nodegroup=nodegroup, name=temp_node_name, graph=self
            )
            newNode = models.Node(
                nodeid=newid,
                name=temp_node_name,
                istopnode=False,
                ontologyclass=None,
                datatype="semantic",
                nodegroup=nodegroup,
                graph=self,
            )
        else:
            newNode = models.Node(
                nodeid=uuid.uuid1(),
                name=temp_node_name,
                istopnode=False,
                ontologyclass=None,
                datatype="semantic",
                graph=self,
            )

        newEdge = models.Edge(
            domainnode=nodeToAppendTo,
            rangenode=newNode,
            ontologyproperty=None,
            graph=self,
        )
        self.add_node(newNode)
        self.add_edge(newEdge)

        self.populate_null_nodegroups()

        # assign the first class and property found
        if self.ontology:
            ontology_classes = self.get_valid_ontology_classes(
                newNode.nodeid, nodeToAppendTo.nodeid
            )
            if len(ontology_classes) > 0:
                newEdge.ontologyproperty = ontology_classes[0]["ontology_property"]
                newNode.ontologyclass = ontology_classes[0]["ontology_classes"][0]
            else:
                raise GraphValidationError(
                    _("Ontology rules don't allow this node to be appended")
                )

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
        self.has_unpublished_changes = True

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
            function_copy = models.FunctionXGraph(
                function=function_x_graph.function, config=config_copy, graph=self
            )
            function_copy.save()

    def copy(self, root=None, set_source=False):
        """
        returns an unsaved copy of self

        """
        nodegroup_map = {}
        copy_of_self = deepcopy(self)

        copy_of_self.publication = None

        if root is not None:
            root["nodegroup_id"] = root["nodeid"]
            root["istopnode"] = True
            root["is_immutable"] = bool(root["is_immutable"] or self.is_copy_immutable)
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
            copy_of_self.edges = {
                edge_id: edge
                for edge_id, edge in copy_of_self.edges.items()
                if edge.domainnode_id in node_ids
            }
            copy_of_self.nodes = {
                node_id: node
                for node_id, node in copy_of_self.nodes.items()
                if node_id in node_ids
            }
            copy_of_self.cards = {
                card_id: card
                for card_id, card in copy_of_self.cards.items()
                if card.nodegroup_id in node_ids
            }
            copy_of_self.widgets = {
                widget_id: widget
                for widget_id, widget in copy_of_self.widgets.items()
                if widget.card.nodegroup_id in node_ids
            }
            for widget_id, widget in copy_of_self.widgets.items():
                if widget.card.nodegroup_id not in node_ids:
                    widget.card = root_card
            copy_of_self.root = root_node
            copy_of_self.name = root_node.name
            copy_of_self.isresource = False
            copy_of_self.resource_instance_lifecycle = None
            copy_of_self.subtitle = ""
            copy_of_self.description = ""
            copy_of_self.author = ""

        # returns a list of node ids sorted by nodes that are collector nodes first and then others last
        node_ids = sorted(
            copy_of_self.nodes,
            key=lambda node_id: copy_of_self.nodes[node_id].is_collector,
            reverse=True,
        )

        for node in copy_of_self.nodes.values():
            node.is_immutable = bool(node.is_immutable or self.is_copy_immutable)

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
            if set_source:
                node.source_identifier_id = node.pk
            node.pk = uuid.uuid1()
            node_map[node_id] = node.pk

            if is_collector:
                old_nodegroup_id = node.nodegroup_id
                node.nodegroup = models.NodeGroup(
                    pk=node.pk,
                    cardinality=node.nodegroup.cardinality,
                    grouping_node=node,
                )
                if old_nodegroup_id not in nodegroup_map:
                    nodegroup_map[old_nodegroup_id] = node.nodegroup_id
                for card in copy_of_self.cards.values():
                    if str(card.nodegroup_id) == str(old_nodegroup_id):
                        new_id = uuid.uuid1()
                        if set_source:
                            card.source_identifier_id = card.pk
                        card_map[card.pk] = new_id
                        card.pk = new_id
                        card.nodegroup = node.nodegroup
                        card.graph = copy_of_self

            else:
                node.nodegroup = None

        for widget in copy_of_self.widgets.values():
            if set_source:
                widget.source_identifier_id = widget.pk

            widget.pk = uuid.uuid1()
            widget.node_id = node_map[widget.node_id]
            widget.card_id = card_map[widget.card_id]

        copy_of_self.populate_null_nodegroups()

        copy_of_self.nodes = {
            node.pk: node for node_id, node in copy_of_self.nodes.items()
        }

        for edge_id, edge in copy_of_self.edges.items():
            if set_source:
                edge.source_identifier_id = edge.pk
            edge.pk = uuid.uuid1()
            edge.graph = copy_of_self
            copied_domainnode = edge.domainnode
            copied_rangenode = edge.rangenode
            # edge.domainnode_id and rangenode_id refer to orignial nodeid - not new id.
            # edge.domainnode and edge.rangenode point to the new copied nodes
            # We have to update those identifiers here
            edge.domainnode_id = edge.domainnode.pk
            edge.rangenode_id = edge.rangenode.pk
            # in Django 3, this breaks the reference to the domainnode and rangenode
            # so we have to repair them here
            edge.domainnode = copied_domainnode
            edge.rangenode = copied_rangenode

        copy_of_self.edges = {
            edge.pk: edge for edge_id, edge in copy_of_self.edges.items()
        }

        for copied_card in copy_of_self.cards.values():
            if (
                str(copied_card.component_id) == "2f9054d8-de57-45cd-8a9c-58bbb1619030"
            ):  # grouping card
                grouped_card_ids = []
                for copied_grouped_card_id in copied_card.config["groupedCardIds"]:
                    grouped_card_id = card_map.get(uuid.UUID(copied_grouped_card_id))

                    if grouped_card_id:
                        grouped_card_ids.append(str(grouped_card_id))

                copied_card.config["groupedCardIds"] = grouped_card_ids

                sorted_widget_ids = []
                for copied_widget_id in copied_card.config["sortedWidgetIds"]:
                    widget_id = card_map.get(uuid.UUID(copied_widget_id))

                    if widget_id:
                        sorted_widget_ids.append(str(widget_id))

                copied_card.config["sortedWidgetIds"] = sorted_widget_ids

        return {
            "copy": copy_of_self,
            "cards": card_map,
            "nodes": node_map,
            "nodegroups": nodegroup_map,
        }

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
                graph_dict["edges"].append(
                    {
                        "domainnode_id": tree["node"]["nodeid"],
                        "rangenode_id": child["node"]["nodeid"],
                    }
                )
                traverse_tree(child)

        tree = JSONSerializer().serializeToPython(self.get_tree(node))
        tree["node"]["istopnode"] = True
        traverse_tree(tree)

        if skip_validation or self.can_append(
            Graph(graph_dict), self.nodes[uuid.UUID(str(newparentnodeid))]
        ):
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

            self.has_unpublished_changes = True
            self.populate_null_nodegroups()
            return ret

    def update_node(self, node):
        """
        updates a node in the graph

        Arguments:
        node -- a python dictionary representing a node object to be used to update the graph

        """
        node["nodeid"] = uuid.UUID(str(node.get("nodeid")))

        if node["source_identifier_id"]:
            node["source_identifier_id"] = uuid.UUID(
                str(node.get("source_identifier_id"))
            )

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

        # new_node will always have a nodegroup id even if if was set to None
        # because populate_null_nodegroups
        # will populate the nodegroup id with the parent nodegroup
        # add/remove a card if a nodegroup was added/removed
        if new_node.nodegroup_id != old_node.nodegroup_id:
            if new_node.is_collector:
                # add a card
                new_card = models.CardModel(
                    name=new_node.name, nodegroup=new_node.nodegroup
                )
                self.add_card(new_card)
            else:
                self._nodegroups_to_delete = [old_node.nodegroup]
                # remove a card
                self.cards = {
                    card_id: card
                    for card_id, card in self.cards.items()
                    if card.nodegroup_id != old_node.nodegroup_id
                }

        try:
            new_card = models.CardModel.objects.get(
                name=old_node.name, nodegroup=new_node.nodegroup
            )
            for cardid, card in self.cards.items():
                if cardid == new_card.cardid:
                    card.name = new_node.name
        except ObjectDoesNotExist:
            pass

        self.has_unpublished_changes = True

        return {"card": new_card, "node": new_node}

    def delete_node(self, node=None):
        """
        deletes a node and all of its children from a graph

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

        self.has_unpublished_changes = True
        super().save()

        return self

    def can_append(self, graphToAppend, nodeToAppendTo):
        """
        can_append - test to see whether or not a graph can be appended to this graph at a specific location

        returns true if the graph can be appended, false otherwise

        Arguments:
        graphToAppend -- the Graph to test appending on to this graph
        nodeToAppendTo -- the node from which to append the graph

        """

        found = False

        if self.ontology is not None and graphToAppend.ontology is None:
            raise GraphValidationError(
                _("The graph you wish to append needs to define an ontology")
            )

        if self.ontology is not None and graphToAppend.ontology is not None:
            for domain_connection in graphToAppend.get_valid_domain_ontology_classes():
                for ontology_class in domain_connection["ontology_classes"]:
                    if ontology_class == nodeToAppendTo.ontologyclass:
                        found = True
                        break

                if found:
                    break

            if not found:
                raise GraphValidationError(
                    _("Ontology rules don't allow this graph to be appended")
                )
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
            incoming_edge = list(
                filter(lambda x: x.rangenode_id == node.nodeid, self.edges.values())
            )[0]
            parent_node_id = incoming_edge.domainnode_id
            sibling_nodes = [
                edge.rangenode
                for edge in filter(
                    lambda x: x.domainnode_id == parent_node_id, self.edges.values()
                )
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
            source = (
                self.nodes[uuid.UUID(str(nodeid))].ontologyclass
                if nodeid is not None
                else self.root.ontologyclass
            )
            ontology_classes = models.OntologyClass.objects.get(
                source=source, ontology=self.ontology
            )
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

            ontology_dict = {
                ontology.source: ontology
                for ontology in models.OntologyClass.objects.filter(
                    source__in=[edge.rangenode.ontologyclass for edge in out_edges],
                    ontology_id=self.ontology_id,
                )
            }

            if len(out_edges) > 0:
                for edge in out_edges:

                    for ontology_property in ontology_dict.get(
                        edge.rangenode.ontologyclass
                    ).target["up"]:
                        if (
                            edge.ontologyproperty
                            == ontology_property["ontology_property"]
                        ):
                            if len(ontology_classes) == 0:
                                ontology_classes = set(
                                    ontology_property["ontology_classes"]
                                )
                            else:
                                ontology_classes = ontology_classes.intersection(
                                    set(ontology_property["ontology_classes"])
                                )

                            if len(ontology_classes) == 0:
                                break

            # get a list of properties (and corresponding classes) that could be used to relate to my parent node
            # limit the list of properties based on the intersection between the property's classes and the list of
            # ontology classes we found above
            if parent_node:
                range_ontologies = models.OntologyClass.objects.get(
                    source=parent_node.ontologyclass, ontology_id=self.ontology_id
                ).target["down"]
                if len(out_edges) == 0:
                    return range_ontologies
                else:
                    for ontology_property in range_ontologies:
                        ontology_property["ontology_classes"] = list(
                            set(ontology_property["ontology_classes"]).intersection(
                                ontology_classes
                            )
                        )

                        if len(ontology_property["ontology_classes"]) > 0:
                            ret.append(ontology_property)

            else:
                # if a brand new resource
                if len(out_edges) == 0:
                    ret = [
                        {
                            "ontology_property": "",
                            "ontology_classes": models.OntologyClass.objects.values_list(
                                "source", flat=True
                            ).filter(
                                ontology_id=self.ontology_id
                            ),
                        }
                    ]
                else:
                    # if no parent node then just use the list of ontology classes from above, there will be no properties to return
                    ret = [
                        {
                            "ontology_property": "",
                            "ontology_classes": list(ontology_classes),
                        }
                    ]
        return ret

    def get_nodegroups(self, force_recalculation=False):
        """
        get the nodegroups associated with this graph

        """
        if self.should_use_published_graph() and not force_recalculation:
            return super().get_nodegroups()
        else:
            nodegroups = set()
            for node in self.nodes.values():
                if node.is_collector:
                    nodegroups.add(node.nodegroup)
            for card in self.cards.values():
                try:
                    nodegroups.add(card.nodegroup)
                except models.NodeGroup.DoesNotExist:
                    pass
            return list(nodegroups)

    def update_permissions_from_serialized_graph(self, serialized_graph):
        if (
            "user_permissions" in serialized_graph
            or "group_permissions" in serialized_graph
        ):
            graph_from_database = Graph.objects.filter(pk=self.pk).first()

            if graph_from_database:
                # update user permissions
                if "user_permissions" in serialized_graph:
                    # first, delete all existing user permissions for graph
                    user_permissions = graph_from_database.get_user_permissions(
                        force_recalculation=True
                    )

                    user_permission_ids_to_delete = []
                    for user_permission_list in user_permissions.values():
                        for user_permission in user_permission_list:
                            user_permission_ids_to_delete.append(user_permission.pk)

                    if user_permission_ids_to_delete:
                        UserObjectPermission.objects.filter(
                            pk__in=user_permission_ids_to_delete
                        ).delete()

                    # then, create permissions from serialized permissions
                    user_permissions = []
                    for user_permission_list in serialized_graph[
                        "user_permissions"
                    ].values():
                        user_permissions.extend(user_permission_list)

                    user_permission_nodegroups = models.NodeGroup.objects.filter(
                        pk__in={
                            user_permission["object_pk"]
                            for user_permission in user_permissions
                        }
                    )
                    user_permission_nodegroup_id_to_nodegroup = {
                        nodegroup.pk: nodegroup
                        for nodegroup in user_permission_nodegroups
                    }

                    user_permissions_to_create = []
                    for user_permission in user_permissions:
                        user_permission["content_object"] = (
                            user_permission_nodegroup_id_to_nodegroup[
                                user_permission["object_pk"]
                            ]
                        )
                        user_permissions_to_create.append(
                            UserObjectPermission(**user_permission)
                        )

                    UserObjectPermission.objects.bulk_create(user_permissions_to_create)

                # update group permissions
                if "group_permissions" in serialized_graph:
                    # first, delete all existing group permissions for graph
                    group_permissions = graph_from_database.get_group_permissions(
                        force_recalculation=True
                    )

                    group_permission_ids_to_delete = []
                    for group_permission_list in group_permissions.values():
                        for group_permission in group_permission_list:
                            group_permission_ids_to_delete.append(group_permission.pk)

                    if group_permission_ids_to_delete:
                        GroupObjectPermission.objects.filter(
                            pk__in=group_permission_ids_to_delete
                        ).delete()

                    # then, create permissions from serialized permissions
                    group_permissions = []
                    for group_permission_list in serialized_graph[
                        "group_permissions"
                    ].values():
                        group_permissions.extend(group_permission_list)

                    group_permission_nodegroups = models.NodeGroup.objects.filter(
                        pk__in={
                            group_permission["object_pk"]
                            for group_permission in group_permissions
                        }
                    )
                    group_permission_nodegroup_id_to_nodegroup = {
                        nodegroup.pk: nodegroup
                        for nodegroup in group_permission_nodegroups
                    }

                    group_permissions_to_create = []
                    for group_permission in group_permissions:
                        group_permission["content_object"] = (
                            group_permission_nodegroup_id_to_nodegroup[
                                group_permission["object_pk"]
                            ]
                        )
                        user_permissions_to_create.append(
                            GroupObjectPermission(**group_permission)
                        )

                    GroupObjectPermission.objects.bulk_create(
                        group_permissions_to_create
                    )

    def get_user_permissions(self, force_recalculation=False):
        """
        get the user permissions associated with this graph

        returns {
            nodegroup.pk: [<UserObjectPermission>, ...],
            ...
        },
        """
        if self.should_use_published_graph() and not force_recalculation:
            published_graph = self.get_published_graph()
            user_permissions = published_graph.serialized_graph["user_permissions"]

            return {
                nodegroup_id: [
                    UserObjectPermission(**serialized_user_permission)
                    for serialized_user_permission in serialized_user_permissions
                ]
                for nodegroup_id, serialized_user_permissions in user_permissions.items()
            }
        else:
            user_permissions = {}

            nodegroup_ids = [
                str(nodegroup.pk)
                for nodegroup in self.get_nodegroups(
                    force_recalculation=force_recalculation
                )
            ]
            user_object_permissions = UserObjectPermission.objects.filter(
                object_pk__in=nodegroup_ids
            )

            for user_object_permission in user_object_permissions:
                if not user_permissions.get(
                    uuid.UUID(user_object_permission.object_pk)
                ):
                    user_permissions[uuid.UUID(user_object_permission.object_pk)] = []

                user_permissions[uuid.UUID(user_object_permission.object_pk)].append(
                    user_object_permission
                )

            return user_permissions

    def get_group_permissions(self, force_recalculation=False):
        """
        get the user permissions associated with this graph

        returns {
            nodegroup.pk: [<UserObjectPermission>, ...],
            ...
        },
        """
        if self.should_use_published_graph() and not force_recalculation:
            published_graph = self.get_published_graph()
            group_permissions = published_graph.serialized_graph["group_permissions"]

            return {
                nodegroup_id: [
                    GroupObjectPermission(**serialized_group_permission)
                    for serialized_group_permission in serialized_group_permissions
                ]
                for nodegroup_id, serialized_group_permissions in group_permissions.items()
            }
        else:
            group_permissions = {}

            nodegroup_ids = [
                str(nodegroup.pk)
                for nodegroup in self.get_nodegroups(
                    force_recalculation=force_recalculation
                )
            ]
            user_object_permissions = GroupObjectPermission.objects.filter(
                object_pk__in=nodegroup_ids
            )

            for user_object_permission in user_object_permissions:
                if not group_permissions.get(
                    uuid.UUID(user_object_permission.object_pk)
                ):
                    group_permissions[uuid.UUID(user_object_permission.object_pk)] = []

                group_permissions[uuid.UUID(user_object_permission.object_pk)].append(
                    user_object_permission
                )

            return group_permissions

    def get_or_create_nodegroup(self, nodegroupid, nodegroups_list=[]):
        """
        get a nodegroup from an id by first looking through the nodes and cards associated with this graph.
        if not found then get the nodegroup instance from the database, otherwise return a new instance of a nodegroup
        This is also the method responsible for setting the grouping_node_id
        on the nodegroup when the first (collector) node is created.

        Keyword Arguments

        nodegroupid -- return a nodegroup with this id
        nodegroups_list -- list of nodegroups from which to filter
        """

        found = None
        for nodegroup in nodegroups_list or self.get_nodegroups():
            if str(nodegroup.nodegroupid) == str(nodegroupid):
                found = nodegroup
                break
        else:
            try:
                found = models.NodeGroup.objects.get(pk=nodegroupid)
            except models.NodeGroup.DoesNotExist:
                found = models.NodeGroup(pk=nodegroupid, grouping_node_id=nodegroupid)

        found.grouping_node_id = found.nodegroupid
        return found

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

    def get_cards(self, use_raw_i18n_json=False, force_recalculation=False):
        """
        get the card data (if any) associated with this graph

        """
        if self.should_use_published_graph() and not force_recalculation:
            return super().get_cards()

        cards = []
        for card in self.cards.values():
            if self.isresource:
                if not card.name:
                    card.name = self.nodes[card.nodegroup_id].name
                if str(card.description) in ["null", ""]:
                    try:
                        card.description = self.nodes[card.nodegroup_id].description
                    except KeyError as e:
                        print(
                            "Error: card.description not accessible, nodegroup_id not in self.nodes: ",
                            e,
                        )
            else:
                if card.nodegroup.parentnodegroup_id is None:
                    card.name = self.name
                    card.description = self.description
                else:
                    if not card.name:
                        card.name = self.nodes[card.nodegroup_id].name
                    if str(card.description) in ["null", ""]:
                        card.description = self.nodes[card.nodegroup_id].description
            card_dict = JSONSerializer().serializeToPython(
                card, use_raw_i18n_json=use_raw_i18n_json
            )
            card_constraints = card.constraintmodel_set.all()
            card_dict["constraints"] = JSONSerializer().serializeToPython(
                card_constraints
            )
            cards.append(card_dict)
        return cards

    def get_widgets(self, use_raw_i18n_json=False, force_recalculation=False):
        """
        get the widget data (if any) associated with this graph

        """
        if self.should_use_published_graph() and not force_recalculation:
            return super().get_card_x_node_x_widgets()
        else:
            widgets = []
            if self.widgets:
                for widget in self.widgets.values():
                    widget_dict = JSONSerializer().serializeToPython(
                        widget, use_raw_i18n_json=use_raw_i18n_json
                    )
                    widgets.append(widget_dict)

            return sorted(widgets, key=lambda k: k["id"])

    def serialize(
        self,
        fields=None,
        exclude=None,
        force_recalculation=False,
        use_raw_i18n_json=False,
        **kwargs,
    ):
        """
        serialize to a different form than used by the internal class structure

        used to append additional values (like parent ontology properties) that
        internal objects (like models.Nodes) don't support

        """
        exclude = [] if exclude is None else exclude
        if self.should_use_published_graph() and not force_recalculation:
            published_graph = self.get_published_graph()
            serialized_graph = published_graph.serialized_graph

            for key in exclude:
                if (
                    serialized_graph.get(key) is not None
                ):  # explicit None comparison so falsey values will still return
                    serialized_graph[key] = None

            return serialized_graph
        else:
            ret = JSONSerializer().handle_model(
                self,
                fields=fields,
                exclude=exclude,
                use_raw_i18n_json=use_raw_i18n_json,
            )
            ret["root"] = self.root

            if "relatable_resource_model_ids" not in exclude:
                ret["relatable_resource_model_ids"] = [
                    str(relatable_node.graph_id)
                    for relatable_node in self.root.get_relatable_resources()
                ]
            else:
                ret.pop("relatable_resource_model_ids", None)

            if "cards" not in exclude:
                cards = self.get_cards(
                    use_raw_i18n_json=use_raw_i18n_json,
                    force_recalculation=force_recalculation,
                )
                ret["cards"] = sorted(
                    cards, key=lambda k: (k["sortorder"] or 0, k["cardid"] or 0)
                )
            else:
                ret.pop("cards", None)

            if "cards_x_nodes_x_widgets" not in exclude:
                ret["cards_x_nodes_x_widgets"] = self.get_widgets(
                    use_raw_i18n_json=use_raw_i18n_json,
                    force_recalculation=force_recalculation,
                )
            else:
                ret.pop("cards_x_nodes_x_widgets", None)

            if "nodegroups" not in exclude:
                nodegroups = self.get_nodegroups(
                    force_recalculation=force_recalculation
                )
                ret["nodegroups"] = sorted(nodegroups, key=lambda k: k.pk)
            else:
                ret.pop("nodegroups", None)

            if "user_permissions" not in exclude:
                ret["user_permissions"] = self.get_user_permissions(
                    force_recalculation=force_recalculation
                )
            else:
                ret.pop("user_permissions", None)

            if "group_permissions" not in exclude:
                ret["group_permissions"] = self.get_group_permissions(
                    force_recalculation=force_recalculation
                )
            else:
                ret.pop("group_permissions", None)

            ret["domain_connections"] = (
                self.get_valid_domain_ontology_classes()
                if "domain_connections" not in exclude
                else ret.pop("domain_connections", None)
            )
            ret["functions"] = (
                models.FunctionXGraph.objects.filter(graph_id=self.graphid)
                if "functions" not in exclude
                else ret.pop("functions", None)
            )

            parentproperties = {self.root.nodeid: ""}

            for edge_id, edge in self.edges.items():
                parentproperties[edge.rangenode_id] = edge.ontologyproperty

            if "edges" not in exclude:
                ret["edges"] = sorted(
                    [edge for edge in self.edges.values()], key=lambda k: k.edgeid
                )
            else:
                ret.pop("edges", None)

            if "nodes" not in exclude:
                nodes = []
                for key, node in self.nodes.items():
                    nodeobj = JSONSerializer().serializeToPython(
                        node, use_raw_i18n_json=use_raw_i18n_json
                    )
                    nodeobj["parentproperty"] = parentproperties[node.nodeid]
                    nodes.append(nodeobj)

                ret["nodes"] = sorted(
                    nodes,
                    key=lambda k: (
                        k["sortorder"] if k["sortorder"] is not None else float("inf"),
                        k["nodeid"],
                    ),
                )
            else:
                ret.pop("nodes", None)

            return JSONSerializer().serializeToPython(
                ret, use_raw_i18n_json=use_raw_i18n_json
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
            names_in_nodegroup = [
                v.name
                for k, v in self.nodes.items()
                if v.nodegroup_id == node.nodegroup_id
            ]
            unique_names_in_nodegroup = {n for n in names_in_nodegroup}
            if len(names_in_nodegroup) > len(unique_names_in_nodegroup):
                message = _(
                    'Duplicate node name: "{0}". All node names in a card must be unique.'.format(
                        node.name
                    )
                )
                raise GraphValidationError(message)
            else:
                sibling_node_names = [
                    node.name for node in self.get_sibling_nodes(node)
                ]
                if node.name in sibling_node_names:
                    message = _(
                        'Duplicate node name: "{0}". All sibling node names must be unique.'.format(
                            node.name
                        )
                    )
                    raise GraphValidationError(message)

    def create_node_alias(self, node):
        """
        Assigns a unique, slugified version of a node's name as that node's alias.
        """
        with connection.cursor() as cursor:
            if node.hascustomalias and node.alias:
                cursor.callproc("__arches_slugify", [node.alias])
                node.alias = cursor.fetchone()[0]
            else:
                cursor.callproc("__arches_slugify", [node.name])
                row = cursor.fetchone()
                aliases = [
                    n.alias for n in self.nodes.values() if node.alias != n.alias
                ]
                node.alias = self.make_name_unique(row[0], aliases, "_n")
                node.hascustomalias = False
        return node.alias

    def validate(self):
        """
        validates certain aspects of resource graphs according to defined rules:
            - The root node of a "Resource" can only be a semantic node, and must be a collector
            - A node group that has child node groups may not itself be a child node group
            - A node group can only have child node groups if the node group only contains semantic nodes
            - If graph has an ontology, nodes must have classes and edges must have properties that are ontologically valid
            - If the graph has no ontology, nodes and edges should have null values for ontology class and property respectively
            - The graph has a slug that unique only to it and its draft_graph
        """
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
                raise GraphValidationError(
                    _(
                        "The top node of your resource graph must have a datatype of 'semantic'."
                    ),
                    998,
                )
        else:
            if self.root.is_collector is False:
                if len(self.nodes) > 1:
                    raise GraphValidationError(
                        _(
                            "If your graph contains more than one node and is not a resource the root must be a collector."
                        ),
                        999,
                    )

        def validate_fieldname(fieldname, fieldnames):
            if node.fieldname == "":
                raise GraphValidationError(_("Field name must not be blank."), 1008)
            if fieldname.replace("_", "").isalnum() is False:
                raise GraphValidationError(
                    _(
                        "Field name must contain only alpha-numeric characters or underscores."
                    ),
                    1010,
                )
            if fieldname[0] == "_" or fieldname[0].isdigit():
                raise GraphValidationError(
                    _("Field name cannot begin with an underscore or number"), 1011
                )
            if len(fieldname) > 10:
                fieldname = fieldname[:10]
            try:
                dupe = fieldnames[fieldname]
                raise GraphValidationError(
                    _(
                        "Field name must be unique to the graph; '{fieldname}' already exists."
                    ).format(**locals()),
                    1009,
                )
            except KeyError:
                fieldnames[fieldname] = True

            return fieldname

        fieldnames = {}
        datatype_factory = DataTypeFactory()

        for node in self.nodes.values():
            self._validate_node_name(node)
            datatype = datatype_factory.get_instance(node.datatype)
            datatype.validate_node(node)
            if node.exportable is True:
                if node.fieldname is not None:
                    validated_fieldname = validate_fieldname(node.fieldname, fieldnames)
                    if validated_fieldname != node.fieldname:
                        node.fieldname = validated_fieldname

        # validate that nodes in a resource graph belong to the ontology assigned to the resource graph
        if self.ontology is not None:
            ontology_classes = self.ontology.ontologyclasses.values_list(
                "source", flat=True
            )

            for node_id, node in self.nodes.items():
                if node.ontologyclass == "":
                    raise GraphValidationError(
                        _("A valid {0} ontology class must be selected").format(
                            self.ontology.name
                        ),
                        1000,
                    )
                if node.ontologyclass not in ontology_classes:
                    raise GraphValidationError(
                        _("'{0}' is not a valid {1} ontology class").format(
                            node.ontologyclass, self.ontology.name
                        ),
                        1001,
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
                ontology_classes = self.ontology.ontologyclasses.get(
                    source=edge.domainnode.ontologyclass
                )
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
                        _(
                            "'{0}' is not found in the {1} ontology or is not a valid ontology property for Entity domain '{2}'."
                        ).format(
                            edge.ontologyproperty,
                            self.ontology.name,
                            edge.domainnode.ontologyclass,
                        ),
                        1004,
                    )
        else:
            for node_id, node in self.nodes.items():
                if node.ontologyclass is not None:
                    raise GraphValidationError(
                        _(
                            "You have assigned ontology classes to your graph nodes but not assigned an ontology to your graph."
                        ),
                        IntegrityCheck.NODE_HAS_ONTOLOGY_GRAPH_DOES_NOT.value,
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
            raise GraphValidationError(
                _("The json-ld context you supplied wasn't formatted correctly."), 1006
            )

        if self.slug is not None:
            graphs_with_matching_slug = (
                models.GraphModel.objects.exclude(slug__isnull=True)
                .exclude(source_identifier__isnull=False)
                .filter(slug=self.slug)
            )
            if (first_matching_graph := graphs_with_matching_slug.first()) and str(
                first_matching_graph.graphid
            ) != str(self.graphid):
                if (
                    not self.source_identifier_id
                    or self.source_identifier_id != first_matching_graph.graphid
                ):
                    raise GraphValidationError(
                        _(
                            "Another resource model already uses the slug '{slug}'"
                        ).format(slug=self.slug),
                        1007,
                    )

    def update_published_graphs(self, user=None, notes=None):
        """
        Changes information in in GraphPublication models without creating
        a new entry in graphs_x_published_graphs table
        """
        if self.source_identifier_id:  # don't update future graphs
            raise Exception(
                "Cannot update graphs with a source_identifier. Please apply updates to the source graph."
            )
        else:
            with transaction.atomic():
                LanguageSynchronizer.synchronize_settings_with_db(
                    update_published_graphs=False
                )

                if self.has_unpublished_changes:
                    self.has_unpublished_changes = False
                    super().save()

                published_graph_edit = models.PublishedGraphEdit.objects.create(
                    publication=self.publication, user=user, notes=notes
                )
                published_graph_edit.save()

                published_graphs = models.PublishedGraph.objects.filter(
                    publication_id=self.publication_id
                )

                for language_tuple in settings.LANGUAGES:
                    translation.activate(language=language_tuple[0])

                    serialized_graph = JSONDeserializer().deserialize(
                        JSONSerializer().serialize(self, force_recalculation=True)
                    )

                    published_graph_query = published_graphs.filter(
                        language=language_tuple[0]
                    )
                    if not len(published_graph_query):
                        published_graph = models.PublishedGraph.objects.create(
                            publication_id=self.publication_id,
                            serialized_graph=serialized_graph,
                            language=models.Language.objects.get(
                                code=language_tuple[0]
                            ),
                        )
                    elif len(published_graph_query) == 1:
                        published_graph = published_graph_query[0]
                        published_graph.serialized_graph = serialized_graph
                        published_graph.save()
                    else:
                        raise GraphPublicationError(
                            message=_(
                                "Multiple published graphs returned for language and publication_id"
                            )
                        )

                    translation.deactivate()

            return self

    def create_draft_graph(self):
        """
        Creates an additional entry in the Graphs table that represents an draft version of the current graph
        """
        with transaction.atomic():
            LanguageSynchronizer.synchronize_settings_with_db(
                update_published_graphs=False
            )

            try:
                previous_draft_graph = Graph.objects.get(
                    source_identifier_id=self.graphid
                )
                previous_draft_graph.delete()
            except Graph.DoesNotExist:
                pass

            graph_copy = self.copy(set_source=True)

            draft_graph = graph_copy["copy"]
            draft_graph.source_identifier_id = self.graphid

            # draft_graphs do not interact with `Resource` objects
            draft_graph.resource_instance_lifecycle = None

            # draft_graphs are never published, so on creation
            # `has_unpublished_changes` should never be true, regardless
            # of the state of the source_graph.
            draft_graph.has_unpublished_changes = False

            draft_graph.root.set_relatable_resources(
                [node.pk for node in self.root.get_relatable_resources()]
            )

            draft_graph.save(validate=False)

            return draft_graph

    def update_from_draft_graph(self, draft_graph):
        """
        Updates the graph with any changes made to the draft_graph,
        deletes the draft_graph and related entities, then creates
        a new draft_graph from the updated graph.
        """
        serialized_source_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(self)
        )
        serialized_draft_graph = JSONDeserializer().deserialize(
            JSONSerializer().serialize(draft_graph)
        )

        node_id_to_node_source_identifier_id = {
            node["nodeid"]: node["source_identifier_id"]
            for node in serialized_draft_graph["nodes"]
            if node["source_identifier_id"]
        }

        card_id_to_card_source_identifier_id = {
            card["cardid"]: card["source_identifier_id"]
            for card in serialized_draft_graph["cards"]
            if card["source_identifier_id"]
        }

        # update cards_x_nodes_x_widgets
        for serialized_card_x_node_x_widget in serialized_draft_graph[
            "cards_x_nodes_x_widgets"
        ]:
            if serialized_card_x_node_x_widget["source_identifier_id"]:
                serialized_card_x_node_x_widget["id"] = serialized_card_x_node_x_widget[
                    "source_identifier_id"
                ]
                serialized_card_x_node_x_widget["source_identifier_id"] = None

            updated_card_id = card_id_to_card_source_identifier_id.get(
                serialized_card_x_node_x_widget["card_id"]
            )
            if updated_card_id:
                serialized_card_x_node_x_widget["card_id"] = updated_card_id

            updated_node_id = node_id_to_node_source_identifier_id.get(
                serialized_card_x_node_x_widget["node_id"]
            )
            if updated_node_id:
                serialized_card_x_node_x_widget["node_id"] = updated_node_id

        # update cards
        for serialized_card in serialized_draft_graph["cards"]:
            if serialized_card["source_identifier_id"]:
                serialized_card["cardid"] = serialized_card["source_identifier_id"]
                serialized_card["source_identifier_id"] = None

            source_nodegroup_id = node_id_to_node_source_identifier_id.get(
                serialized_card["nodegroup_id"]
            )
            if source_nodegroup_id:
                serialized_card["nodegroup_id"] = source_nodegroup_id

            serialized_card["graph_id"] = serialized_source_graph["graphid"]

        # update nodes
        for serialized_node in serialized_draft_graph["nodes"]:
            if serialized_node["source_identifier_id"]:
                serialized_node["nodeid"] = serialized_node["source_identifier_id"]
                serialized_node["source_identifier_id"] = None

            updated_nodegroup_id = node_id_to_node_source_identifier_id.get(
                serialized_node["nodegroup_id"]
            )
            if updated_nodegroup_id:
                serialized_node["nodegroup_id"] = updated_nodegroup_id

            serialized_node["graph_id"] = serialized_source_graph["graphid"]

        # update nodegroups
        for serialized_nodegroup in serialized_draft_graph["nodegroups"]:
            updated_nodegroup_id = node_id_to_node_source_identifier_id.get(
                serialized_nodegroup["nodegroupid"]
            )
            if updated_nodegroup_id:
                serialized_nodegroup["nodegroupid"] = updated_nodegroup_id

            updated_parent_nodegroup_id = node_id_to_node_source_identifier_id.get(
                serialized_nodegroup["parentnodegroup_id"]
            )
            if updated_nodegroup_id:
                serialized_nodegroup["parentnodegroup_id"] = updated_parent_nodegroup_id

            updated_grouping_node_id = node_id_to_node_source_identifier_id.get(
                serialized_nodegroup["grouping_node_id"]
            )
            if updated_grouping_node_id:
                serialized_nodegroup["grouping_node_id"] = updated_grouping_node_id

        # update edges
        for serialized_edge in serialized_draft_graph["edges"]:
            if serialized_edge["source_identifier_id"]:
                serialized_edge["edgeid"] = serialized_edge["source_identifier_id"]
                serialized_edge["source_identifier_id"] = None

            source_domain_node_id = node_id_to_node_source_identifier_id.get(
                serialized_edge["domainnode_id"]
            )
            if source_domain_node_id:
                serialized_edge["domainnode_id"] = source_domain_node_id

            source_range_node_id = node_id_to_node_source_identifier_id.get(
                serialized_edge["rangenode_id"]
            )
            if source_range_node_id:
                serialized_edge["rangenode_id"] = source_range_node_id

            serialized_edge["graph_id"] = serialized_source_graph["graphid"]

        # update root node
        serialized_draft_graph["root"]["graph_id"] = serialized_source_graph["graphid"]
        serialized_draft_graph["root"]["nodeid"] = serialized_draft_graph["root"][
            "source_identifier_id"
        ]
        serialized_draft_graph["root"]["source_identifier_id"] = None

        # update graph data
        serialized_draft_graph["graphid"] = serialized_source_graph["graphid"]
        serialized_draft_graph["resource_instance_lifecycle_id"] = (
            serialized_source_graph["resource_instance_lifecycle_id"]
        )
        serialized_draft_graph["source_identifier_id"] = None

        # update permissions
        serialized_draft_graph["group_permissions"] = {
            key: value
            for key, value in serialized_source_graph["group_permissions"].items()
            if key in node_id_to_node_source_identifier_id.values()
        }
        serialized_draft_graph["user_permissions"] = {
            key: value
            for key, value in serialized_source_graph["user_permissions"].items()
            if key in node_id_to_node_source_identifier_id.values()
        }

        serialized_draft_graph["relatable_resource_model_ids"] = [
            (
                serialized_source_graph["graphid"]
                if relatable_resource_model_id == serialized_draft_graph["graphid"]
                else relatable_resource_model_id
            )
            for relatable_resource_model_id in serialized_draft_graph[
                "relatable_resource_model_ids"
            ]
        ]

        return self.restore_state_from_serialized_graph(serialized_draft_graph)

    def restore_state_from_serialized_graph(self, serialized_graph):
        """
        Restores a Graph's state from a serialized graph, and creates a
        new draft_graph
        """
        with transaction.atomic():
            draft_graph = Graph.objects.filter(source_identifier_id=self.pk).first()
            if draft_graph:
                draft_graph.delete()

            self.delete_associated_entities()

            for serialized_nodegroup in serialized_graph["nodegroups"]:
                for key, value in serialized_nodegroup.items():
                    try:
                        serialized_nodegroup[key] = uuid.UUID(value)
                    except:
                        pass

                nodegroup = models.NodeGroup(**serialized_nodegroup)
                nodegroup.save()

            for serialized_node in serialized_graph["nodes"]:
                for key, value in serialized_node.items():
                    try:
                        serialized_node[key] = uuid.UUID(value)
                    except:
                        pass

                del serialized_node["is_collector"]
                del serialized_node["parentproperty"]

                node = models.Node(**serialized_node)
                node.save()

            for serialized_edge in serialized_graph["edges"]:
                for key, value in serialized_edge.items():
                    try:
                        serialized_edge[key] = uuid.UUID(value)
                    except:
                        pass

                edge = models.Edge(**serialized_edge)
                edge.save()

            for serialized_card in serialized_graph["cards"]:
                for key, value in serialized_card.items():
                    try:
                        serialized_card[key] = uuid.UUID(value)
                    except:
                        pass

                del serialized_card["constraints"]

                if "is_editable" in serialized_card:
                    del serialized_card["is_editable"]

                card = Card(**serialized_card)
                card.save()

            widget_dict = {}
            for serialized_widget in serialized_graph.get(
                "widgets", serialized_graph.get("cards_x_nodes_x_widgets")
            ):
                for key, value in serialized_widget.items():
                    try:
                        serialized_widget[key] = uuid.UUID(value)
                    except:
                        pass

                updated_widget = models.CardXNodeXWidget(**serialized_widget)
                updated_widget.save()

                widget_dict[updated_widget.pk] = updated_widget

            updated_graph = Graph(serialized_graph)
            updated_graph.widgets = widget_dict
            updated_graph.is_active = self.is_active

            updated_graph.update_permissions_from_serialized_graph(serialized_graph)

            relatable_resource_model_nodes = models.Node.objects.filter(
                graph_id__in=serialized_graph["relatable_resource_model_ids"],
                istopnode=True,
            )
            updated_graph.root.set_relatable_resources(
                list(
                    {
                        node.source_identifier.pk if node.source_identifier else node.pk
                        for node in relatable_resource_model_nodes
                    }
                )
            )

            updated_graph.has_unpublished_changes = False
            updated_graph.save(validate=False)

            updated_graph.create_draft_graph()

            return Graph.objects.get(pk=updated_graph.pk)

    def publish(self, user=None, notes=None):
        """
        Adds a corresponding entry to the GraphXPublishedGraph table,
        and creates a PublishedGraph entry for every active language
        """
        if self.source_identifier_id:
            raise RuntimeError("Publishing a draft_graph is prohibited.")

        self.refresh_from_database()

        with transaction.atomic():
            publication = models.GraphXPublishedGraph.objects.create(
                graph=self, notes=notes, user=user
            )

            self.publication = publication
            self.has_unpublished_changes = False

            super().save()  # avoids side-effects from `Graph.save`

            for language_tuple in settings.LANGUAGES:
                language = models.Language.objects.get(code=language_tuple[0])

                translation.activate(language=language_tuple[0])

                models.PublishedGraph.objects.create(
                    publication=publication,
                    serialized_graph=JSONDeserializer().deserialize(
                        JSONSerializer().serialize(self, force_recalculation=True)
                    ),
                    language=language,
                )

            translation.deactivate()


class GraphPublicationError(Exception):
    def __init__(self, message, code=None):
        self.title = _("Graph Publication Error")
        self.message = message
        self.code = code

    def __str__(self):
        return repr(self.message)


class GraphValidationError(Exception):
    def __init__(self, message, code=None):
        self.title = _("Graph Validation Error")
        self.message = message
        self.code = code

    def __str__(self):
        return repr(self.message)
