"""Publication lifecycle operations against a real graph.

The inverse of spike_tests.test_package_migration_is_reverted_by_promoting_a_stale_draft:
there, a migration was silently undone by the next Graph Designer publish. Here,
RefreshDraftGraph closes that loop.
"""

import uuid

from arches.app.models import models
from arches.app.models.graph import Graph
from arches.db.package_migrations.operations.edge import CreateEdge
from arches.db.package_migrations.operations.node import CreateNode
from arches.db.package_migrations.operations.publish import (
    PublishGraph,
    RefreshDraftGraph,
    RepointResourceInstances,
)

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

    def test_repoint_moves_resources_between_publications(self):
        resource = models.ResourceInstance.objects.create(graph=self.graph)
        old_publication_id = self.graph.publication_id
        new_publication_id = uuid.uuid4()

        PublishGraph(
            graphid=str(self.graph.graphid), publication_id=str(new_publication_id)
        ).database_forwards("arches", self.schema_editor, self._state(), self._state())

        resource.refresh_from_db()
        self.assertEqual(resource.graph_publication_id, old_publication_id)

        affected = RepointResourceInstances(
            graphid=str(self.graph.graphid),
            from_publication_id=str(old_publication_id),
            to_publication_id=str(new_publication_id),
        ).database_forwards("arches", self.schema_editor, self._state(), self._state())

        self.assertEqual(affected, 1)
        resource.refresh_from_db()
        self.assertEqual(resource.graph_publication_id, new_publication_id)

    def test_refresh_draft_graph_prevents_the_migration_being_reverted(self):
        """The fix for the fatal finding.

        Without RefreshDraftGraph the next promote_draft_graph_to_active_graph()
        rebuilds the live graph from a draft that predates the migration, silently
        undoing it. With it, the draft already contains the migration's changes.
        """
        nodeid = uuid.uuid4()
        CreateNode(
            graphid=str(self.graph.graphid),
            nodeid=str(nodeid),
            name="Survey Date",
            datatype="date",
            alias="survey_date_lifecycle",
            nodegroup_id=str(self.nodegroup_id),
        ).database_forwards("arches", self.schema_editor, self._state(), self._state())
        # A non-collector node needs an edge joining it to the tree, or
        # populate_null_nodegroups() cannot reach it when the graph is copied.
        CreateEdge(
            graphid=str(self.graph.graphid),
            edgeid=str(uuid.uuid4()),
            domainnode_id=str(self.nodegroup_id),
            rangenode_id=str(nodeid),
            ontologyproperty="http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by",
        ).database_forwards("arches", self.schema_editor, self._state(), self._state())

        RefreshDraftGraph(graphid=str(self.graph.graphid)).database_forwards(
            "arches", self.schema_editor, self._state(), self._state()
        )

        graph = Graph.objects.get(pk=self.graph.graphid)
        graph.promote_draft_graph_to_active_graph()

        self.assertTrue(
            models.Node.objects.filter(
                graph_id=self.graph.graphid, alias="survey_date_lifecycle"
            ).exists(),
            "RefreshDraftGraph must keep the draft in step so a later publish "
            "does not revert the migration",
        )
