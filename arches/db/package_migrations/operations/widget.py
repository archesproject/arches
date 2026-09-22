"""Card-x-node-x-widget operations.

Which widget renders a node, its label, visibility and sort order are ordinary
Graph Designer edits that touch no node and no card.

I18n note: label is an I18n_TextField and config is an I18n_JSONField, so values
for them must be explicit {lang: value} dicts.
"""

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
