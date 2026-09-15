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
    has_graph_fk = False

    def describe(self):
        return "Create widget assignment %s" % self._pk

    @property
    def migration_name_fragment(self):
        return "widget_%s" % self._pk.replace("-", "")[:8]


class AlterCardXNodeXWidget(_AlterRowOperation):
    model = models.CardXNodeXWidget
    state_collection = "widgets"
    pk_attribute = "id"

    def __init__(self, graphid, id, changes):
        super().__init__(graphid, changes)
        self.id = id

    def describe(self):
        return "Alter widget assignment %s (%s)" % (
            self.id,
            ", ".join(sorted(self.changes)),
        )

    @property
    def migration_name_fragment(self):
        return "alter_widget_%s" % str(self.id).replace("-", "")[:8]


class DeleteCardXNodeXWidget(_DeleteRowOperation):
    model = models.CardXNodeXWidget
    state_collection = "widgets"
    pk_field = "id"
    has_graph_fk = False

    def describe(self):
        return "Delete widget assignment %s" % self.pk

    @property
    def migration_name_fragment(self):
        return "delete_widget_%s" % str(self.pk).replace("-", "")[:8]
