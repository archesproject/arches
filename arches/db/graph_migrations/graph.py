"""MigrationGraph.make_state() hardcodes ProjectState, so it is overridden here."""

from django.db.migrations.graph import MigrationGraph

from arches.db.graph_migrations.state import GraphState


class GraphMigrationGraph(MigrationGraph):
    state_class = GraphState

    def make_state(self, nodes=None, at_end=True, real_apps=None):
        if nodes is None:
            nodes = list(self.leaf_nodes())
        if not nodes:
            return self.state_class()
        if not isinstance(nodes[0], tuple):
            nodes = [nodes]
        plan = self._generate_plan(nodes, at_end)
        graph_state = self.state_class()
        for node in plan:
            graph_state = self.nodes[node].mutate_state(graph_state, preserve=False)
        return graph_state
