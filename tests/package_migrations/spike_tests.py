"""Stage 0.5 spike: exercise real package-migration operations against a real
Arches graph, so stage 4's per-operation estimate rests on something measured.

Also pins the draft-graph behaviour that makes RefreshDraftGraph mandatory.
"""

import uuid

from arches.app.models import models
from arches.app.models.graph import Graph
from arches.db.package_migrations.operations.data import BackfillNodeData
from arches.db.package_migrations.operations.node import CreateNode, DeleteNode
from arches.db.package_migrations.state import PackageState

from tests.base_test import ArchesTestCase


class _FakeSchemaEditor:
    """Operations only use schema_editor.connection.alias."""

    def __init__(self, connection):
        self.connection = connection


class PackageMigrationOperationTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_graph = cls.create_test_graph()

    @classmethod
    def create_test_graph(cls):
        """A resource graph with one collector nodegroup holding a string node.

        Built directly rather than by appending a branch, because these are the
        same primitives CreateNodeGroup/CreateNode use.
        """
        graph = Graph.objects.create_graph(name="SPIKE RESOURCE", is_resource=True)

        collector_id = uuid.uuid4()
        nodegroup = models.NodeGroup.objects.create(
            nodegroupid=collector_id, cardinality="n"
        )
        # node_groups.grouping_node_matches_pk_or_null: grouping_node must be the
        # nodegroup's own pk, so the collector node shares the nodegroup id.
        models.Node.objects.create(
            nodeid=collector_id,
            graph_id=graph.graphid,
            nodegroup_id=collector_id,
            name="Spike Group",
            datatype="semantic",
            alias="spike_group",
            hascustomalias=True,
            istopnode=False,
        )
        models.NodeGroup.objects.filter(pk=collector_id).update(
            grouping_node_id=collector_id
        )
        models.CardModel.objects.create(
            graph_id=graph.graphid, nodegroup_id=collector_id, name="Spike Card"
        )
        string_node = models.Node.objects.create(
            nodeid=uuid.uuid4(),
            graph_id=graph.graphid,
            nodegroup_id=collector_id,
            name="Spike String",
            datatype="string",
            alias="spike_string",
            hascustomalias=True,
            istopnode=False,
        )
        # Edges are not optional. Graph.copy() nulls every non-collector node's
        # nodegroup and then rebuilds membership with populate_null_nodegroups(),
        # which walks the EDGE tree -- so a graph whose nodes are not joined by
        # edges cannot be copied, drafted or promoted.
        models.Edge.objects.create(
            edgeid=uuid.uuid4(),
            graph_id=graph.graphid,
            domainnode_id=graph.root.nodeid,
            rangenode_id=collector_id,
            ontologyproperty="http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
        )
        models.Edge.objects.create(
            edgeid=uuid.uuid4(),
            graph_id=graph.graphid,
            domainnode_id=collector_id,
            rangenode_id=string_node.nodeid,
            ontologyproperty="http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
        )
        graph = Graph.objects.get(pk=graph.graphid)
        graph.publish()
        return Graph.objects.get(pk=graph.graphid)

    def setUp(self):
        from django.db import connection

        self.schema_editor = _FakeSchemaEditor(connection)
        self.graph = Graph.objects.get(pk=self.test_graph.graphid)
        self.string_node = [
            n for n in self.graph.nodes.values() if n.datatype == "string"
        ][0]
        self.nodegroup_id = self.string_node.nodegroup_id

    def _state(self):
        state = PackageState()
        state.add_graph(
            {"graphid": str(self.graph.graphid), "slug": self.graph.slug, "nodes": {}}
        )
        return state

    def _make_tile(self):
        resource = models.ResourceInstance.objects.create(graph=self.graph)
        return models.TileModel.objects.create(
            resourceinstance=resource,
            nodegroup_id=self.nodegroup_id,
            data={
                str(self.string_node.nodeid): {"en": {"value": "x", "direction": "ltr"}}
            },
        )

    def test_create_node_writes_a_real_row_and_keeps_the_alias(self):
        nodeid = uuid.uuid4()
        op = CreateNode(
            graphid=str(self.graph.graphid),
            fields={
                "nodeid": str(nodeid),
                "name": "Survey Date",
                "datatype": "date",
                "istopnode": False,
                "alias": "survey_date",
                "nodegroup_id": str(self.nodegroup_id),
            },
        )
        state = self._state()
        op.state_forwards("arches", state)
        op.database_forwards("arches", self.schema_editor, self._state(), state)

        node = models.Node.objects.get(pk=nodeid)
        self.assertEqual(node.datatype, "date")
        # The alias must survive exactly: deriving it at apply time would run the
        # __arches_slugify stored procedure and make it install-dependent.
        self.assertEqual(node.alias, "survey_date")
        self.assertEqual(str(node.graph_id), str(self.graph.graphid))
        self.assertIn(str(nodeid), state.graphs[str(self.graph.graphid)]["nodes"])

    def test_create_node_reverses_cleanly(self):
        nodeid = uuid.uuid4()
        op = CreateNode(
            graphid=str(self.graph.graphid),
            fields={
                "nodeid": str(nodeid),
                "name": "Temp",
                "datatype": "string",
                "istopnode": False,
                "alias": "temp_node",
                "nodegroup_id": str(self.nodegroup_id),
            },
        )
        op.database_forwards("arches", self.schema_editor, self._state(), self._state())
        self.assertTrue(models.Node.objects.filter(pk=nodeid).exists())
        op.database_backwards(
            "arches", self.schema_editor, self._state(), self._state()
        )
        self.assertFalse(models.Node.objects.filter(pk=nodeid).exists())

    def test_backfill_adds_the_key_only_where_absent_and_is_idempotent(self):
        tile = self._make_tile()
        new_nodeid = str(uuid.uuid4())

        op = BackfillNodeData(
            nodegroup_id=str(self.nodegroup_id), nodeid=new_nodeid, value=None
        )
        affected = op.database_forwards(
            "arches", self.schema_editor, self._state(), self._state()
        )
        self.assertEqual(affected, 1)

        tile.refresh_from_db()
        self.assertIn(new_nodeid, tile.data)
        self.assertIsNone(tile.data[new_nodeid])

        # Re-running matches nothing: the content predicate IS the version test.
        self.assertEqual(
            op.database_forwards(
                "arches", self.schema_editor, self._state(), self._state()
            ),
            0,
        )

    def test_backfill_reverses(self):
        tile = self._make_tile()
        new_nodeid = str(uuid.uuid4())
        op = BackfillNodeData(
            nodegroup_id=str(self.nodegroup_id), nodeid=new_nodeid, value=None
        )
        op.database_forwards("arches", self.schema_editor, self._state(), self._state())
        op.database_backwards(
            "arches", self.schema_editor, self._state(), self._state()
        )
        tile.refresh_from_db()
        self.assertNotIn(new_nodeid, tile.data)

    def test_tile_save_readds_keys_for_live_nodes(self):
        """Pins why RemoveNodeData must run AFTER DeleteNode.

        TileModel.save() -> set_missing_keys_to_none() reads live Node rows and
        re-adds any missing key, so stripping data while the node still exists is
        undone by the next ordinary save.
        """
        tile = self._make_tile()
        nodeid = uuid.uuid4()
        CreateNode(
            graphid=str(self.graph.graphid),
            fields={
                "nodeid": str(nodeid),
                "name": "Ghost",
                "datatype": "string",
                "istopnode": False,
                "alias": "ghost_node",
                "nodegroup_id": str(self.nodegroup_id),
            },
        ).database_forwards("arches", self.schema_editor, self._state(), self._state())

        models.TileModel.objects.filter(pk=tile.pk).update(
            data={str(self.string_node.nodeid): None}
        )
        tile.refresh_from_db()
        self.assertNotIn(str(nodeid), tile.data)

        tile.save()
        tile.refresh_from_db()
        self.assertIn(str(nodeid), tile.data)

    def test_package_migration_is_reverted_by_promoting_a_stale_draft(self):
        """The finding that makes RefreshDraftGraph mandatory.

        A package migration mutates the live graph. The draft copy is untouched,
        so the next Graph Designer publish promotes the stale draft and the
        migration's node disappears.
        """
        nodeid = uuid.uuid4()
        CreateNode(
            graphid=str(self.graph.graphid),
            fields={
                "nodeid": str(nodeid),
                "name": "Survey Date",
                "datatype": "date",
                "istopnode": False,
                "alias": "survey_date_2",
                "nodegroup_id": str(self.nodegroup_id),
            },
        ).database_forwards("arches", self.schema_editor, self._state(), self._state())
        self.assertTrue(models.Node.objects.filter(pk=nodeid).exists())

        graph = Graph.objects.get(pk=self.test_graph.graphid)
        if graph.get_draft_graph() is None:
            graph.create_draft_graph()
        graph = Graph.objects.get(pk=self.test_graph.graphid)
        graph.promote_draft_graph_to_active_graph()

        self.assertFalse(
            models.Node.objects.filter(pk=nodeid).exists(),
            "expected the stale draft promotion to revert the package migration",
        )
