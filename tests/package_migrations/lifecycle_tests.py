"""Publication lifecycle operations against a real graph.

The inverse of spike_tests.test_package_migration_is_reverted_by_promoting_a_stale_draft:
there, a migration was silently undone by the next Graph Designer publish. Here,
Reconciling the draft after a run closes that loop.
"""

import uuid

from django.db import connection

from arches.app.models import models
from arches.app.models.graph import Graph
from arches.db.package_migrations.operations.edge import CreateEdge
from arches.db.package_migrations.operations.node import CreateNode
from arches.db.package_migrations.operations.nodegroup import CreateNodeGroup
from arches.db.package_migrations.operations.resource import SetResourcePublication
from arches.db.package_migrations import drafts
from arches.db.package_migrations.operations.graph import CreateGraph, PublishGraph

from tests.package_migrations.spike_tests import (
    PackageMigrationOperationTests,
    _FakeSchemaEditor,
)


class PublicationLifecycleTests(PackageMigrationOperationTests):
    def test_publish_graph_uses_the_supplied_publication_id(self):
        """Portable publication ids: the same migration produces the same
        publication id on every install, so 'which version is this site on' is
        answerable across installs."""
        publication_id = uuid.uuid4()
        PublishGraph(
            graphid=str(self.graph.graphid), publication_id=str(publication_id)
        ).database_forwards("arches", self.schema_editor, self._state(), self._state())

        graph = models.GraphModel.objects.get(pk=self.graph.graphid)
        self.assertEqual(graph.publication_id, publication_id)
        self.assertTrue(
            models.GraphXPublishedGraph.objects.filter(pk=publication_id).exists()
        )

    def test_resources_move_onto_the_publication_and_back(self):
        """Publishing and stamping resources are two operations. Reverse order is
        load-bearing: unapply() reverses operation order, so resources come off the
        publication (PROTECT) before PublishGraph deletes it."""
        resource = models.ResourceInstance.objects.create(graph=self.graph)
        old_publication_id = self.graph.publication_id
        publication_id = str(uuid.uuid4())
        publish = PublishGraph(
            graphid=str(self.graph.graphid),
            publication_id=publication_id,
            previous_publication_id=str(old_publication_id),
        )
        stamp = SetResourcePublication(
            graphid=str(self.graph.graphid),
            publication_id=publication_id,
            previous_publication_id=str(old_publication_id),
        )

        for operation in (publish, stamp):
            operation.database_forwards(
                "arches", self.schema_editor, self._state(), self._state()
            )
        resource.refresh_from_db()
        self.assertEqual(str(resource.graph_publication_id), publication_id)

        for operation in (stamp, publish):
            operation.database_backwards(
                "arches", self.schema_editor, self._state(), self._state()
            )
        resource.refresh_from_db()
        self.assertEqual(resource.graph_publication_id, old_publication_id)
        self.assertFalse(
            models.GraphXPublishedGraph.objects.filter(pk=publication_id).exists()
        )

    def test_nodegroup_can_be_created_before_its_grouping_node(self):
        nodegroupid = str(uuid.uuid4())
        graphid = str(self.graph.graphid)
        CreateNodeGroup(
            graphid=graphid,
            fields={"nodegroupid": nodegroupid, "grouping_node_id": nodegroupid},
        ).database_forwards("arches", self.schema_editor, self._state(), self._state())
        CreateNode(
            graphid=graphid,
            fields={
                "nodeid": nodegroupid,
                "name": "Survey",
                "datatype": "semantic",
                "istopnode": False,
                "alias": "survey_grouping",
                "nodegroup_id": nodegroupid,
            },
        ).database_forwards("arches", self.schema_editor, self._state(), self._state())

        with connection.cursor() as cursor:
            # TestCase never commits, so run the deferred FK checks now.
            cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
        self.assertEqual(
            str(models.NodeGroup.objects.get(pk=nodegroupid).grouping_node_id),
            nodegroupid,
        )

    def test_reconciling_the_draft_stops_a_later_publish_reverting_the_migration(self):
        """The fix for the fatal finding.

        Without it the next promote_draft_graph_to_active_graph() rebuilds the live
        graph from a draft that predates the migration, silently undoing it. The
        draft is derived state, so migratepkg reconciles it once per run rather
        than carrying an operation that could never be reversed.
        """
        nodeid = uuid.uuid4()
        CreateNode(
            graphid=str(self.graph.graphid),
            fields={
                "nodeid": str(nodeid),
                "name": "Survey Date",
                "datatype": "date",
                "istopnode": False,
                "alias": "survey_date_lifecycle",
                "nodegroup_id": str(self.nodegroup_id),
            },
        ).database_forwards("arches", self.schema_editor, self._state(), self._state())
        # A non-collector node needs an edge joining it to the tree, or
        # populate_null_nodegroups() cannot reach it when the graph is copied.
        CreateEdge(
            graphid=str(self.graph.graphid),
            fields={
                "edgeid": str(uuid.uuid4()),
                "domainnode_id": str(self.nodegroup_id),
                "rangenode_id": str(nodeid),
                "ontologyproperty": "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            },
        ).database_forwards("arches", self.schema_editor, self._state(), self._state())

        drafts.reconcile([str(self.graph.graphid)], "default")

        graph = Graph.objects.get(pk=self.graph.graphid)
        graph.promote_draft_graph_to_active_graph()

        self.assertTrue(
            models.Node.objects.filter(
                graph_id=self.graph.graphid, alias="survey_date_lifecycle"
            ).exists(),
            "reconciling the draft must keep it in step so a later publish does "
            "not revert the migration",
        )

    def test_creating_a_graph_reverses_only_while_it_holds_no_resources(self):
        """Reversing a CreateGraph deletes the graph, and ResourceInstance.graph is
        CASCADE, so on a fresh install it is ordinary, and on a site with data it
        is the destruction of every resource on that model."""
        graphid = str(uuid.uuid4())
        operation = CreateGraph(
            fields={
                "graphid": graphid,
                "name": "Throwaway",
                "slug": "throwaway_%s" % graphid[:8],
                "isresource": True,
            }
        )
        operation.database_forwards(
            "arches", self.schema_editor, self._state(), self._state()
        )
        self.assertTrue(models.GraphModel.objects.filter(pk=graphid).exists())

        resource = models.ResourceInstance.objects.create(graph_id=graphid)
        with self.assertRaises(ValueError):
            operation.database_backwards(
                "arches", self.schema_editor, self._state(), self._state()
            )
        self.assertTrue(models.GraphModel.objects.filter(pk=graphid).exists())

        resource.delete()
        operation.database_backwards(
            "arches", self.schema_editor, self._state(), self._state()
        )
        self.assertFalse(models.GraphModel.objects.filter(pk=graphid).exists())
