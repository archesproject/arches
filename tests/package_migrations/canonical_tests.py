"""Canonical projection: shape, stability, and agreement with the operations.

No database.
"""

import uuid

from django.test import SimpleTestCase

from arches.app.models import models
from arches.db.package_migrations.canonical import (
    canonical_graph,
    fields_for,
    graph_hash,
)
from arches.db.package_migrations.state import PackageState
from arches.db.package_migrations.operations.card import CreateCard
from arches.db.package_migrations.operations.edge import CreateEdge
from arches.db.package_migrations.operations.graph import CreateGraph
from arches.db.package_migrations.operations.node import CreateNode
from arches.db.package_migrations.operations.nodegroup import CreateNodeGroup
from arches.db.package_migrations.operations.widget import CreateCardXNodeXWidget

GRAPH = str(uuid.uuid4())
NODE = str(uuid.uuid4())
NODEGROUP = str(uuid.uuid4())
EDGE = str(uuid.uuid4())
CARD = str(uuid.uuid4())
WIDGET = str(uuid.uuid4())


def _serialized_graph():
    return {
        "graphid": GRAPH,
        "name": {"en": "Heritage Asset"},
        "slug": "heritage-asset",
        "isresource": True,
        # derived / install-local keys that must NOT survive the projection
        "relatable_resource_model_ids": {GRAPH},
        "domain_connections": [{"whatever": 1}],
        "functions_x_graphs": [{"id": 1}],
        "spatial_views": [{"slug": "sv"}],
        "user_permissions": {"1": []},
        "group_permissions": {"2": []},
        "nodes": [
            {
                "nodeid": NODE,
                "name": {"en": "Survey Date"},
                "datatype": "date",
                "istopnode": False,
                "alias": "survey_date",
                "nodegroup_id": NODEGROUP,
                "graph_id": GRAPH,
                "is_collector": False,
                "parentproperty": "P1",
                "source_identifier_id": str(uuid.uuid4()),
            }
        ],
        "nodegroups": [{"nodegroupid": NODEGROUP, "cardinality": "n"}],
        "edges": [
            {
                "edgeid": EDGE,
                "domainnode_id": NODE,
                "rangenode_id": NODE,
                "graph_id": GRAPH,
                "ontologyproperty": "P1",
            }
        ],
        "cards": [
            {
                "cardid": CARD,
                "nodegroup_id": NODEGROUP,
                "graph_id": GRAPH,
                "constraints": [{"x": 1}],
                "is_editable": True,
            }
        ],
        "cards_x_nodes_x_widgets": [
            {"id": WIDGET, "card_id": CARD, "node_id": NODE, "widget_id": WIDGET}
        ],
    }


class CanonicalProjectionTests(SimpleTestCase):
    def test_collections_are_keyed_maps(self):
        canonical = canonical_graph(_serialized_graph())
        self.assertEqual(set(canonical["nodes"]), {NODE})
        self.assertEqual(set(canonical["nodegroups"]), {NODEGROUP})
        self.assertEqual(set(canonical["edges"]), {EDGE})
        self.assertEqual(set(canonical["cards"]), {CARD})
        self.assertEqual(set(canonical["widgets"]), {WIDGET})

    def test_derived_and_install_local_keys_are_dropped(self):
        canonical = canonical_graph(_serialized_graph())
        for key in (
            "relatable_resource_model_ids",
            "domain_connections",
            "functions_x_graphs",
            "spatial_views",
            "user_permissions",
            "group_permissions",
        ):
            self.assertNotIn(key, canonical, key)
        node = canonical["nodes"][NODE]
        for key in (
            "is_collector",
            "parentproperty",
            "graph_id",
            "source_identifier_id",
        ):
            self.assertNotIn(key, node, key)
        card = canonical["cards"][CARD]
        for key in ("constraints", "is_editable", "graph_id"):
            self.assertNotIn(key, card, key)

    def test_hash_is_stable_across_key_and_list_ordering(self):
        """A projection that hashed differently per ordering would make
        --check churn forever."""
        first = _serialized_graph()
        second = _serialized_graph()
        second["nodes"] = list(reversed(second["nodes"]))
        second["name"] = {"en": "Heritage Asset"}
        self.assertEqual(
            graph_hash(canonical_graph(first)), graph_hash(canonical_graph(second))
        )

    def test_hash_changes_when_content_changes(self):
        changed = _serialized_graph()
        changed["nodes"][0]["datatype"] = "concept"
        self.assertNotEqual(
            graph_hash(canonical_graph(_serialized_graph())),
            graph_hash(canonical_graph(changed)),
        )

    def test_sets_and_tuples_normalize(self):
        graph = _serialized_graph()
        graph["nodes"][0]["config"] = {"options": ("b", "a"), "ids": {2, 1}}
        node = canonical_graph(graph)["nodes"][NODE]
        self.assertEqual(node["config"], {"options": ["b", "a"], "ids": [1, 2]})


class OperationStateMatchesProjectionTests(SimpleTestCase):
    """The drift guard.

    A Create* operation stores the canonical row verbatim, so the guard is that
    the projection's field set for each model is exactly what the corresponding
    model declares. If they ever disagree, every makepkgmigrations run reports a
    phantom change that no migration can resolve.
    """

    def test_projection_covers_every_package_content_column(self):
        from arches.db.package_migrations.canonical import EXCLUDED_FIELDS

        for model in (
            models.GraphModel,
            models.Node,
            models.NodeGroup,
            models.Edge,
            models.CardModel,
            models.CardXNodeXWidget,
        ):
            with self.subTest(model=model.__name__):
                declared = {f.attname for f in model._meta.concrete_fields}
                projected = set(fields_for(model))
                self.assertEqual(projected, declared - EXCLUDED_FIELDS)

    def test_create_operations_store_the_canonical_row_verbatim(self):
        canonical = canonical_graph(_serialized_graph())
        state = PackageState()
        CreateGraph(
            fields={
                key: value
                for key, value in canonical.items()
                if key not in ("nodes", "nodegroups", "edges", "cards", "widgets")
            }
        ).state_forwards("arches", state)

        for operation, collection, key in (
            (CreateNodeGroup, "nodegroups", NODEGROUP),
            (CreateNode, "nodes", NODE),
            (CreateEdge, "edges", EDGE),
            (CreateCard, "cards", CARD),
            (CreateCardXNodeXWidget, "widgets", WIDGET),
        ):
            with self.subTest(op=operation.__name__):
                operation(
                    graphid=GRAPH, fields=canonical[collection][key]
                ).state_forwards("arches", state)
                self.assertEqual(
                    state.graphs[GRAPH][collection][key], canonical[collection][key]
                )
