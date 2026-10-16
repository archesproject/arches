from arches.app.models import models
from arches.db.package_migrations.operations.base import (
    _AlterRowOperation,
    _CreateRowOperation,
    _DeleteRowOperation,
)


class CreateCard(_CreateRowOperation):
    model = models.CardModel
    verbose_name = "card"


class AlterCard(_AlterRowOperation):
    model = models.CardModel
    verbose_name = "card"


class DeleteCard(_DeleteRowOperation):
    model = models.CardModel
    verbose_name = "card"
