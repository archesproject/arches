"""Card operations.

Card text, helptext, sortorder and visibility are among the most common Graph
Designer edits and change independently of any node or nodegroup.

A collector nodegroup with no CardModel is invisible and uneditable in the
resource editor, because the card API filters
graph.cardmodel_set.filter(nodegroup__in=permitted_nodegroups). Nothing creates a
card automatically outside Graph.append_node(), so the diff must always pair
CreateNodeGroup with CreateCard.

I18n note: name, description, instructions, helptitle and helptext are
I18n_TextFields. Values for them must be explicit {lang: value} dicts; a bare
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
    verbose_name = "card"


class AlterCard(_AlterRowOperation):
    model = models.CardModel
    verbose_name = "card"


class DeleteCard(_DeleteRowOperation):
    model = models.CardModel
    verbose_name = "card"
