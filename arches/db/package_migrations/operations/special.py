"""Escape hatch for changes no operation expresses.

Mirrors django.db.migrations.RunPython, with one documented difference: there is
no historical model registry for package data, so the callable receives live
models. A package migration written against today's models may need revisiting
when those models change -- which is the honest trade for having an escape hatch
at all.
"""

from arches.db.package_migrations.operations.base import PackageOperation


class RunPackagePython(PackageOperation):
    def __init__(self, code, reverse_code=None, hints=None):
        self.code = code
        self.reverse_code = reverse_code
        self.hints = hints

    @property
    def reversible(self):
        return self.reverse_code is not None

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        return self.code(schema_editor, to_state)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        if self.reverse_code is None:
            raise NotImplementedError("This package migration is not reversible.")
        return self.reverse_code(schema_editor, to_state)

    def describe(self):
        return "Run custom package migration code"

    @property
    def migration_name_fragment(self):
        return "run_python"
