"""Node operations. Structural only: tile keys are the data operations' job."""

from arches.app.models import models
from arches.db.package_migrations.operations.base import (
    _AlterRowOperation,
    _CreateRowOperation,
    _DeleteRowOperation,
    _short,
)


class CreateNode(_CreateRowOperation):
    model = models.Node
    verbose_name = "node"

    @property
    def _label(self):
        return f"{self.fields.get('alias')} ({self.fields.get('datatype')})"

    @property
    def _fragment(self):
        return self.fields.get("alias") or _short(self._pk)


class AlterNode(_AlterRowOperation):
    model = models.Node
    verbose_name = "node"


class DeleteNode(_DeleteRowOperation):
    model = models.Node
    verbose_name = "node"
