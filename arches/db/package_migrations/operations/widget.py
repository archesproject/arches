from arches.app.models import models
from arches.db.package_migrations.operations.base import (
    _AlterRowOperation,
    _CreateRowOperation,
    _DeleteRowOperation,
)


class CreateCardXNodeXWidget(_CreateRowOperation):
    model = models.CardXNodeXWidget
    verbose_name = "widget"


class AlterCardXNodeXWidget(_AlterRowOperation):
    model = models.CardXNodeXWidget
    verbose_name = "widget"


class DeleteCardXNodeXWidget(_DeleteRowOperation):
    model = models.CardXNodeXWidget
    verbose_name = "widget"
