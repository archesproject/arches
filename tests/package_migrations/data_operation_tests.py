"""Data operations: whether recording one instead of running it would skip
anything, and moving resources between publications."""

import uuid

from arches.app.models import models
from arches.app.models.graph import Graph
from arches.db.package_migrations.operations.base import PackageMigrationError
from arches.db.package_migrations.operations.python import RunPackagePython
from arches.db.package_migrations.operations.resource import SetResourcePublication
from arches.db.package_migrations.operations.tile import (
    AddNodeToTiles,
    DeleteTilesForNodeGroup,
    RemoveNodeFromTiles,
)

from tests.package_migrations.spike_tests import PackageMigrationOperationTests


class PendingWorkTests(PackageMigrationOperationTests):
    def test_add_node_to_tiles_has_work_until_every_tile_has_the_key(self):
        operation = AddNodeToTiles(
            nodegroup_id=str(self.nodegroup_id), nodeid=str(uuid.uuid4())
        )
        self.assertFalse(operation.has_pending_work("default"))
        self._make_tile()
        self.assertTrue(operation.has_pending_work("default"))
        operation.database_forwards("arches", self.schema_editor, None, None)
        self.assertFalse(operation.has_pending_work("default"))

    def test_remove_node_from_tiles_has_work_while_data_or_edits_could_hold_it(self):
        tile = self._make_tile()
        nodeid = str(self.string_node.nodeid)
        operation = RemoveNodeFromTiles(
            nodegroup_id=str(self.nodegroup_id), nodeid=nodeid
        )
        self.assertTrue(operation.has_pending_work("default"))

        models.TileModel.objects.filter(pk=tile.pk).update(data={})
        self.assertFalse(operation.has_pending_work("default"))

        models.TileModel.objects.filter(pk=tile.pk).update(
            provisionaledits={"1": {"value": {nodeid: "edit"}}}
        )
        self.assertTrue(operation.has_pending_work("default"))

    def test_delete_tiles_for_nodegroup_has_work_while_tiles_remain(self):
        operation = DeleteTilesForNodeGroup(nodegroup_id=str(self.nodegroup_id))
        self.assertFalse(operation.has_pending_work("default"))
        self._make_tile()
        self.assertTrue(operation.has_pending_work("default"))

    def test_set_resource_publication_has_work_while_resources_lag_the_graph(self):
        operation = SetResourcePublication(
            graphid=str(self.graph.graphid),
            publication_id=str(uuid.uuid4()),
            previous_publication_id=None,
        )
        models.ResourceInstance.objects.create(graph=self.graph)
        self.assertFalse(operation.has_pending_work("default"))

        Graph.objects.get(pk=self.graph.graphid).publish()
        self.assertTrue(operation.has_pending_work("default"))

    def test_custom_code_always_has_work(self):
        operation = RunPackagePython(code=lambda schema_editor, state: None)
        self.assertTrue(operation.has_pending_work("default"))


class SetResourcePublicationBackwardsTests(PackageMigrationOperationTests):
    def test_every_resource_goes_back_to_the_previous_publication(self):
        """Including resources on a publication this migration never made, which
        is where a Designer publish leaves them on the authoring database."""
        previous_publication_id = str(self.graph.publication_id)
        on_previous = models.ResourceInstance.objects.create(graph=self.graph)
        Graph.objects.get(pk=self.graph.graphid).publish()
        on_designer_publication = models.ResourceInstance.objects.create(
            graph=Graph.objects.get(pk=self.graph.graphid)
        )
        self.assertNotEqual(
            str(on_designer_publication.graph_publication_id), previous_publication_id
        )

        SetResourcePublication(
            graphid=str(self.graph.graphid),
            publication_id=str(uuid.uuid4()),
            previous_publication_id=previous_publication_id,
        ).database_backwards("arches", self.schema_editor, None, None)

        for resource in (on_previous, on_designer_publication):
            resource.refresh_from_db()
            self.assertEqual(
                str(resource.graph_publication_id), previous_publication_id
            )

    def test_refuses_a_previous_publication_this_database_never_had(self):
        operation = SetResourcePublication(
            graphid=str(self.graph.graphid),
            publication_id=str(uuid.uuid4()),
            previous_publication_id=str(uuid.uuid4()),
        )
        with self.assertRaises(PackageMigrationError):
            operation.database_backwards("arches", self.schema_editor, None, None)
