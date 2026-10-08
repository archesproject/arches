"""Publication lifecycle operations against a real graph."""

import uuid

from django.db import connection

from arches.app.models import models
from arches.app.models.graph import Graph
from arches.db.package_migrations.operations.base import PackageMigrationError
from arches.db.package_migrations.operations.edge import CreateEdge
from arches.db.package_migrations.operations.node import CreateNode
from arches.db.package_migrations.operations.nodegroup import CreateNodeGroup
from arches.db.package_migrations.operations.graph import CreateGraph, PublishGraph

from tests.package_migrations.spike_tests import PackageMigrationOperationTests


class PublicationLifecycleTests(PackageMigrationOperationTests):
    def test_publish_graph_uses_the_supplied_publication_id(self):
        publication_id = uuid.uuid4()
        PublishGraph(
            graphid=str(self.graph.graphid), publication_id=str(publication_id)
        ).database_forwards("arches", self.schema_editor, self._state(), self._state())

        graph = models.GraphModel.objects.get(pk=self.graph.graphid)
        self.assertEqual(graph.publication_id, publication_id)
        self.assertTrue(
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

    def test_discarding_the_draft_stops_a_later_publish_reverting_the_migration(self):
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
        # Graph.copy() rebuilds nodegroups by walking edges, so every node needs one.
        CreateEdge(
            graphid=str(self.graph.graphid),
            fields={
                "edgeid": str(uuid.uuid4()),
                "domainnode_id": str(self.nodegroup_id),
                "rangenode_id": str(nodeid),
                "ontologyproperty": "http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
            },
        ).database_forwards("arches", self.schema_editor, self._state(), self._state())

        graph = Graph.objects.get(pk=self.graph.graphid)
        graph.delete_draft_graph()

        graph = Graph.objects.get(pk=self.graph.graphid)
        graph.create_draft_graph()

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
        graphid = str(uuid.uuid4())
        operation = CreateGraph(
            fields={
                "graphid": graphid,
                "name": "Throwaway",
                "slug": f"throwaway_{graphid[:8]}",
                "isresource": True,
            }
        )
        operation.database_forwards(
            "arches", self.schema_editor, self._state(), self._state()
        )
        self.assertTrue(models.GraphModel.objects.filter(pk=graphid).exists())

        resource = models.ResourceInstance.objects.create(graph_id=graphid)
        with self.assertRaises(PackageMigrationError):
            operation.database_backwards(
                "arches", self.schema_editor, self._state(), self._state()
            )
        self.assertTrue(models.GraphModel.objects.filter(pk=graphid).exists())

        resource.delete()
        operation.database_backwards(
            "arches", self.schema_editor, self._state(), self._state()
        )
        self.assertFalse(models.GraphModel.objects.filter(pk=graphid).exists())
