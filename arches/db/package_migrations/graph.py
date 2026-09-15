"""MigrationGraph is not reusable verbatim.

``MigrationGraph.make_state()`` hardcodes ``ProjectState`` (django graph.py:326
and :330), so the only way for the loader to hand a PackageState to
``Operation.state_forwards()`` is to subclass and override it.
"""

from django.db.migrations.graph import MigrationGraph

from arches.db.package_migrations.state import PackageState


class PackageMigrationGraph(MigrationGraph):
    state_class = PackageState

    def make_state(self, nodes=None, at_end=True, real_apps=None):
        # Mirrors MigrationGraph.make_state with state_class in place of
        # ProjectState. _generate_plan is private Django API; the version-pinning
        # test in tests/package_migrations guards against it changing shape.
        if nodes is None:
            nodes = list(self.leaf_nodes())
        if not nodes:
            return self.state_class()
        if not isinstance(nodes[0], tuple):
            nodes = [nodes]
        plan = self._generate_plan(nodes, at_end)
        package_state = self.state_class(real_apps=real_apps)
        for node in plan:
            package_state = self.nodes[node].mutate_state(package_state, preserve=False)
        return package_state
