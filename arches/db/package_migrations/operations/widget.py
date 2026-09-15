"""Card-x-node-x-widget operations.

Which widget renders a node, its label, visibility and sort order are ordinary
Graph Designer edits that touch no node and no card, so they get their own
operations.

I18n note: label is an I18n_TextField and config is an I18n_JSONField; kwargs
targeting them must be explicit {lang: value} dicts.
"""

from arches.app.models import models
from arches.db.package_migrations.operations.base import (
    PackageOperation,
    _AlterRowOperation,
)


class CreateCardXNodeXWidget(PackageOperation):
    reversible = True

    def __init__(
        self,
        graphid,
        id,
        card_id,
        node_id,
        widget_id,
        label=None,
        config=None,
        visible=True,
        sortorder=None,
    ):
        self.graphid = graphid
        self.id = id
        self.card_id = card_id
        self.node_id = node_id
        self.widget_id = widget_id
        self.label = label
        self.config = config
        self.visible = visible
        self.sortorder = sortorder

    def _fields(self):
        return {
            "id": str(self.id),
            "card_id": str(self.card_id),
            "node_id": str(self.node_id),
            "widget_id": str(self.widget_id),
            "label": self.label,
            "config": self.config,
            "visible": self.visible,
            "sortorder": self.sortorder,
        }

    def state_forwards(self, app_label, state):
        state.graphs[str(self.graphid)].setdefault("widgets", {})[
            str(self.id)
        ] = self._fields()

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        self.qs(models.CardXNodeXWidget, schema_editor).create(**self._fields())

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        self.qs(models.CardXNodeXWidget, schema_editor).filter(pk=self.id).delete()

    def describe(self):
        return "Create widget assignment %s" % self.id

    @property
    def migration_name_fragment(self):
        return "widget_%s" % str(self.id).replace("-", "")[:8]


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


class DeleteCardXNodeXWidget(PackageOperation):
    reversible = True

    def __init__(self, graphid, id):
        self.graphid = graphid
        self.id = id

    def state_forwards(self, app_label, state):
        del state.graphs[str(self.graphid)]["widgets"][str(self.id)]

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        self.qs(models.CardXNodeXWidget, schema_editor).filter(pk=self.id).delete()

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        widget = dict(to_state.graphs[str(self.graphid)]["widgets"][str(self.id)])
        self.qs(models.CardXNodeXWidget, schema_editor).create(**widget)

    def describe(self):
        return "Delete widget assignment %s" % self.id

    @property
    def migration_name_fragment(self):
        return "delete_widget_%s" % str(self.id).replace("-", "")[:8]
