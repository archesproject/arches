"""Graph operations.

CreateGraph uses models.GraphModel.objects.create(), NOT
Graph.objects.create_graph(). The latter mints a random root nodeid, publishes
with a random publicationid and creates a second GraphModel row (a draft), none
of which a migration can predict or reproduce on another install -- and the
leftover draft then makes Graph.validate() raise code 1019 for every later
operation in the same migration.

(The NotImplementedError guard lives on the Graph PROXY's manager;
models.GraphModel.objects is a plain manager.)
"""

from django.conf import settings

from arches.app.models import models
from arches.db.package_migrations.operations.base import (
    PackageOperation,
    _AlterRowOperation,
)

COLLECTIONS = ("nodes", "nodegroups", "edges", "cards", "widgets")


class CreateGraph(PackageOperation):
    # Irreversible: deleting a graph CASCADEs through ResourceInstance to every
    # tile on it. Removing a graph is a deliberate, separately-confirmed act, not
    # the reverse of a migration.
    reversible = False

    serialization_expand_args = ["fields"]

    def __init__(self, fields):
        # The graph's own id lives in fields, like every other row's pk.
        self.fields = fields

    @property
    def graphid(self):
        return str(self.fields["graphid"])

    def state_forwards(self, app_label, state):
        graph = dict(self.fields)
        graph["graphid"] = self.graphid
        graph.update({collection: {} for collection in COLLECTIONS})
        state.add_graph(graph)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        fields = dict(self.fields)
        if fields.get("resource_instance_lifecycle_id") is None and fields.get(
            "isresource"
        ):
            # graphs.resource_instance_lifecycle_conditional_null requires a
            # non-null lifecycle on every non-draft resource graph.
            fields["resource_instance_lifecycle_id"] = (
                settings.DEFAULT_RESOURCE_INSTANCE_LIFECYCLE_ID
            )
        self.qs(models.GraphModel, schema_editor).create(**fields)

    def describe(self):
        return "Create graph %s" % (self.fields.get("slug") or self.graphid)

    @property
    def migration_name_fragment(self):
        return "graph_%s" % (
            self.fields.get("slug") or self.graphid.replace("-", "")[:8]
        )


class AlterGraph(_AlterRowOperation):
    """Graph metadata and ontology.

    Writes through a queryset update rather than Graph.save(): validate() raises
    code 1018 ("You cannot change the slug of a published graph").
    """

    model = models.GraphModel
    state_collection = None  # the graph dict itself, not a collection on it

    @property
    def _pk(self):
        return self.graphid

    def _entry(self, state):
        return state.graph(self.graphid)

    def describe(self):
        return "Alter graph %s (%s)" % (self.graphid, ", ".join(sorted(self.changes)))

    @property
    def migration_name_fragment(self):
        return "alter_graph_%s" % str(self.graphid).replace("-", "")[:8]
