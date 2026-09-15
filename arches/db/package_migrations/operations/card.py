"""Card operations.

Card text, helptext, sortorder and visibility are among the most common Graph
Designer edits and change independently of any node or nodegroup.

A collector nodegroup with no CardModel is invisible and uneditable in the
resource editor, because the card API filters
graph.cardmodel_set.filter(nodegroup__in=permitted_nodegroups). Nothing creates a
card automatically outside Graph.append_node(), so the autodetector must always
pair CreateNodeGroup with CreateCard.

I18n note: name, description, instructions, helptitle and helptext are
I18n_TextFields. Values for them must be explicit {lang: value} dicts -- a bare
string is stored under whichever language happens to be active on the target.
"""

from arches.app.models import models
from arches.db.package_migrations.operations.base import (
    _AlterRowOperation,
    _CreateRowOperation,
    _DeleteRowOperation,
)


class CreateCard(_CreateRowOperation):
    model = models.CardModel
    state_collection = "cards"
    pk_field = "cardid"

    def describe(self):
        return "Create card %s on graph %s" % (self._pk, self.graphid)

    @property
    def migration_name_fragment(self):
        return "card_%s" % self._pk.replace("-", "")[:8]


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


class DeleteCard(_DeleteRowOperation):
    model = models.CardModel
    state_collection = "cards"
    pk_field = "cardid"

    def describe(self):
        return "Delete card %s from graph %s" % (self.pk, self.graphid)

    @property
    def migration_name_fragment(self):
        return "delete_card_%s" % str(self.pk).replace("-", "")[:8]
