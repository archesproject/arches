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
    state_collection = "widgets"
    pk_field = "id"
    verbose_name = "widget"
    has_graph_fk = False


class AlterCardXNodeXWidget(_AlterRowOperation):
    model = models.CardXNodeXWidget
    state_collection = "widgets"
    pk_attribute = "id"
    verbose_name = "widget"

    def __init__(self, graphid, id, changes):
        super().__init__(graphid, changes)
        self.id = id


class DeleteCardXNodeXWidget(_DeleteRowOperation):
    model = models.CardXNodeXWidget
    state_collection = "widgets"
    verbose_name = "widget"
    has_graph_fk = False
