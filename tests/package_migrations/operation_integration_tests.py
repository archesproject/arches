"""Package migration operations against a real graph, and the draft-graph
behaviour that makes draft reconciliation mandatory."""

import uuid

from django.db import connection

from arches.app.models import models
from arches.app.models.graph import Graph
from arches.db.package_migrations.operations.tile import (
    AddNodeToTiles,
    RemoveNodeFromTiles,
)
from arches.db.package_migrations.operations.node import CreateNode
from arches.db.package_migrations.state import PackageState

from tests.base_test import ArchesTestCase


class _FakeSchemaEditor:
    def __init__(self, connection):
        self.connection = connection


class PackageMigrationOperationTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_graph = cls.create_test_graph()

    @classmethod
    def create_test_graph(cls):
        graph = Graph.objects.create_graph(name="SPIKE RESOURCE", is_resource=True)

        collector_id = uuid.uuid4()
        models.NodeGroup.objects.create(nodegroupid=collector_id, cardinality="n")
        # The collector node shares the nodegroup id: grouping_node_matches_pk_or_null.
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
        # Graph.copy() rebuilds nodegroups by walking edges, so every node needs one.
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


class NodeAndTileOperationTests(PackageMigrationOperationTests):
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

        op = AddNodeToTiles(
            nodegroup_id=str(self.nodegroup_id), nodeid=new_nodeid, value=None
        )
        affected = op.database_forwards(
            "arches", self.schema_editor, self._state(), self._state()
        )
        self.assertEqual(affected, 1)

        tile.refresh_from_db()
        self.assertIn(new_nodeid, tile.data)
        self.assertIsNone(tile.data[new_nodeid])

        self.assertEqual(
            op.database_forwards(
                "arches", self.schema_editor, self._state(), self._state()
            ),
            0,
        )

    def test_removing_a_node_also_clears_it_from_provisional_edits(self):
        doomed = str(uuid.uuid4())
        keeper = str(uuid.uuid4())
        tile = self._make_tile()
        tile.data[doomed] = "gone soon"
        tile.provisionaledits = {
            "7f3b4e2a-0000-4000-8000-00000000000a": {
                "status": "pending",
                "value": {doomed: "pending value", keeper: "keep me"},
            },
            "7f3b4e2a-0000-4000-8000-00000000000b": {"status": "pending"},
        }
        models.TileModel.objects.filter(pk=tile.pk).update(
            data=tile.data, provisionaledits=tile.provisionaledits
        )

        RemoveNodeFromTiles(
            nodegroup_id=str(self.nodegroup_id), nodeid=doomed
        ).database_forwards("arches", self.schema_editor, self._state(), self._state())

        tile.refresh_from_db()
        self.assertNotIn(doomed, tile.data)
        edits = tile.provisionaledits
        self.assertNotIn(doomed, edits["7f3b4e2a-0000-4000-8000-00000000000a"]["value"])
        self.assertIn(keeper, edits["7f3b4e2a-0000-4000-8000-00000000000a"]["value"])
        self.assertEqual(
            edits["7f3b4e2a-0000-4000-8000-00000000000b"], {"status": "pending"}
        )

    def test_backfill_reverses(self):
        tile = self._make_tile()
        new_nodeid = str(uuid.uuid4())
        op = AddNodeToTiles(
            nodegroup_id=str(self.nodegroup_id), nodeid=new_nodeid, value=None
        )
        op.database_forwards("arches", self.schema_editor, self._state(), self._state())
        op.database_backwards(
            "arches", self.schema_editor, self._state(), self._state()
        )
        tile.refresh_from_db()
        self.assertNotIn(new_nodeid, tile.data)

    def test_tile_save_readds_keys_for_live_nodes(self):
        """Pins why RemoveNodeFromTiles must run after DeleteNode."""
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
