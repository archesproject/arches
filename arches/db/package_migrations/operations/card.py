"""Card operations.

Card text, helptext, sortorder and visibility are among the most common Graph
Designer edits and change independently of any node or nodegroup, so cards get
their own Create/Alter/Delete.

I18n note: name, description, instructions, helptitle and helptext are
I18n_TextFields. Operation kwargs targeting them must be explicit {lang: value}
dicts -- a bare string would be stored under whichever language happens to be
active on the target install.
"""

from arches.app.models import models
from arches.db.package_migrations.operations.base import (
    PackageOperation,
    _AlterRowOperation,
)

DEFAULT_CARD_COMPONENT_ID = "f05e4d3a-53c1-11e8-b0ea-784f435179ea"


class CreateCard(PackageOperation):
    reversible = True

    def __init__(
        self,
        graphid,
        cardid,
        nodegroup_id,
        name=None,
        description=None,
        instructions=None,
        helpenabled=False,
        helptitle=None,
        helptext=None,
        cssclass=None,
        active=True,
        visible=True,
        sortorder=None,
        component_id=DEFAULT_CARD_COMPONENT_ID,
    ):
        self.graphid = graphid
        self.cardid = cardid
        self.nodegroup_id = nodegroup_id
        self.name = name
        self.description = description
        self.instructions = instructions
        self.helpenabled = helpenabled
        self.helptitle = helptitle
        self.helptext = helptext
        self.cssclass = cssclass
        self.active = active
        self.visible = visible
        self.sortorder = sortorder
        self.component_id = component_id

    def _fields(self):
        return {
            "cardid": str(self.cardid),
            "nodegroup_id": str(self.nodegroup_id),
            "name": self.name,
            "description": self.description,
            "instructions": self.instructions,
            "helpenabled": self.helpenabled,
            "helptitle": self.helptitle,
            "helptext": self.helptext,
            "cssclass": self.cssclass,
            "active": self.active,
            "visible": self.visible,
            "sortorder": self.sortorder,
            "component_id": self.component_id,
        }

    def state_forwards(self, app_label, state):
        state.graphs[str(self.graphid)].setdefault("cards", {})[
            str(self.cardid)
        ] = self._fields()

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        self.qs(models.CardModel, schema_editor).create(
            graph_id=self.graphid, **self._fields()
        )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        self.qs(models.CardModel, schema_editor).filter(pk=self.cardid).delete()

    def describe(self):
        return "Create card %s on graph %s" % (self.cardid, self.graphid)

    @property
    def migration_name_fragment(self):
        return "card_%s" % str(self.cardid).replace("-", "")[:8]


class AlterCard(_AlterRowOperation):
    model = models.CardModel
    state_collection = "cards"
    pk_attribute = "cardid"

    def __init__(self, graphid, cardid, changes):
        super().__init__(graphid, changes)
        self.cardid = cardid

    def describe(self):
        return "Alter card %s (%s)" % (self.cardid, ", ".join(sorted(self.changes)))

    @property
    def migration_name_fragment(self):
        return "alter_card_%s" % str(self.cardid).replace("-", "")[:8]


class DeleteCard(PackageOperation):
    reversible = True

    def __init__(self, graphid, cardid):
        self.graphid = graphid
        self.cardid = cardid

    def state_forwards(self, app_label, state):
        del state.graphs[str(self.graphid)]["cards"][str(self.cardid)]

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        self.qs(models.CardModel, schema_editor).filter(pk=self.cardid).delete()

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        card = dict(to_state.graphs[str(self.graphid)]["cards"][str(self.cardid)])
        self.qs(models.CardModel, schema_editor).create(graph_id=self.graphid, **card)

    def describe(self):
        return "Delete card %s from graph %s" % (self.cardid, self.graphid)

    @property
    def migration_name_fragment(self):
        return "delete_card_%s" % str(self.cardid).replace("-", "")[:8]
