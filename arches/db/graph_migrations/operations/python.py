"""Like RunPython, but the callable receives live models: there is no historical
registry for graph migrations."""

from arches.db.graph_migrations.operations.base import GraphOperation


class RunGraphPython(GraphOperation):
    scope = "data"

    def __init__(self, code, reverse_code=None):
        self.code = code
        self.reverse_code = reverse_code

    @property
    def reversible(self):
        return self.reverse_code is not None

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        return self.code(schema_editor, to_state)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        if self.reverse_code is None:
            raise NotImplementedError("This graph migration is not reversible.")
        return self.reverse_code(schema_editor, to_state)

    def describe(self):
        return "Run custom graph migration code"

    @property
    def migration_name_fragment(self):
        return "run_python"
