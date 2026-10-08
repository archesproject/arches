"""MigrationGraph.make_state() hardcodes ProjectState, so it is overridden here."""

from django.db.migrations.graph import MigrationGraph

from arches.db.package_migrations.state import PackageState


class PackageMigrationGraph(MigrationGraph):
    state_class = PackageState

    def make_state(self, nodes=None, at_end=True, real_apps=None):
        if nodes is None:
            nodes = list(self.leaf_nodes())
        if not nodes:
            return self.state_class()
        if not isinstance(nodes[0], tuple):
            nodes = [nodes]
        plan = self._generate_plan(nodes, at_end)
        package_state = self.state_class()
        for node in plan:
            package_state = self.nodes[node].mutate_state(package_state, preserve=False)
        return package_state
