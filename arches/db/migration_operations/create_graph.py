from arches.app.models.graph import Graph

from .base import ArchesDataMigration


class CreateGraph(ArchesDataMigration):
    reduces_to_sql = False
    reversible = True

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
        Graph.objects.filter(graphid=self.graphid).delete()

    def describe(self):
        return "Creates a graph with id %s" % self.graphid

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
