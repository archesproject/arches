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


class CreateGraph(PackageOperation):
    # Irreversible: deleting a graph CASCADEs through ResourceInstance to every
    # tile on it. Removing a graph is a deliberate, separately-confirmed act, not
    # the reverse of a migration.
    reversible = False

    def __init__(
        self,
        graphid,
        name,
        slug=None,
        is_resource=True,
        subtitle=None,
        description=None,
        author=None,
        version=None,
        iconclass=None,
        ontology_id=None,
        resource_instance_lifecycle_id=None,
    ):
        self.graphid = graphid
        self.name = name
        self.slug = slug
        self.is_resource = is_resource
        self.subtitle = subtitle
        self.description = description
        self.author = author
        self.version = version
        self.iconclass = iconclass
        self.ontology_id = ontology_id
        # graphs.resource_instance_lifecycle_conditional_null requires a non-null
        # lifecycle on every non-draft resource graph.
        self.resource_instance_lifecycle_id = resource_instance_lifecycle_id

    def state_forwards(self, app_label, state):
        state.add_graph(
            {
                "graphid": str(self.graphid),
                "slug": self.slug,
                "name": self.name,
                "is_resource": self.is_resource,
                "subtitle": self.subtitle,
                "description": self.description,
                "author": self.author,
                "version": self.version,
                "iconclass": self.iconclass,
                "ontology_id": self.ontology_id,
                "nodes": {},
                "nodegroups": {},
                "edges": {},
                "cards": {},
                "widgets": {},
            }
        )

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        lifecycle_id = self.resource_instance_lifecycle_id
        if lifecycle_id is None and self.is_resource:
            lifecycle_id = settings.DEFAULT_RESOURCE_INSTANCE_LIFECYCLE_ID
        self.qs(models.GraphModel, schema_editor).create(
            graphid=self.graphid,
            name=self.name,
            slug=self.slug,
            isresource=self.is_resource,
            subtitle=self.subtitle,
            description=self.description,
            author=self.author,
            version=self.version,
            iconclass=self.iconclass,
            ontology_id=self.ontology_id,
            resource_instance_lifecycle_id=lifecycle_id,
        )

    def describe(self):
        return "Create graph %s" % (self.slug or self.name)

    @property
    def migration_name_fragment(self):
        return "graph_%s" % (self.slug or str(self.graphid).replace("-", "")[:8])


class AlterGraph(_AlterRowOperation):
    """Graph metadata and ontology.

    Note slug: Graph.validate() raises code 1018 ("You cannot change the slug of a
    published graph"), which is why this writes through a queryset update rather
    than Graph.save().
    """

    model = models.GraphModel
    state_collection = None  # the graph dict itself, not a collection on it

    def __init__(self, graphid, changes):
        super().__init__(graphid, changes)

    @property
    def _pk(self):
        return self.graphid

    def _entry(self, state):
        return state.graphs[str(self.graphid)]

    def describe(self):
        return "Alter graph %s (%s)" % (self.graphid, ", ".join(sorted(self.changes)))

    @property
    def migration_name_fragment(self):
        return "alter_graph_%s" % str(self.graphid).replace("-", "")[:8]
