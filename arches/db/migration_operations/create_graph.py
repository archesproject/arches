from arches.app.models.graph import Graph

from .base import ArchesPackageMigration


class CreateGraph(ArchesPackageMigration):
    reduces_to_sql = False
    # Reversing a graph creation means deleting the graph, and ResourceInstance.graph
    # is on_delete=CASCADE, so the delete takes every resource instance and tile with
    # it.  ResourceInstance.graph_publication is on_delete=PROTECT specifically to stop
    # that; nulling it to get past the ProtectedError removes the only guard.
    reversible = False

    def __init__(self, graphid, graph_slug, name="", is_resource=False):
        self.graphid = graphid
        self.graph_slug = graph_slug
        self.name = name
        self.is_resource = is_resource

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        Graph.objects.create_graph(
            graphid=self.graphid,
            slug=self.graph_slug,
            name=self.name,
            is_resource=self.is_resource,
        )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        raise NotImplementedError(
            "CreateGraph is not reversible. Deleting a graph cascades to every "
            "resource instance and tile on it; use a purpose-built, confirmed "
            "operation if a graph genuinely needs to be removed."
        )

    def describe(self):
        return f"Creates a graph with id {self.graphid}"

    @staticmethod
    def as_migration_string(op: dict) -> str:
        return "\n".join(
            [
                "        CreateGraph(",
                f"            graph_id={op['graph_id']!r},",
                f"            graph_slug={op['graph_slug']!r},",
                f"            name={op['name']!r},",
                "        ),",
            ]
        )
