"""Edge operations.

An edge carries the ontology relationship between two nodes and changes
independently of either (ontologyproperty can be corrected without the nodes
moving), so it gets its own operations.
"""

from arches.app.models import models
from arches.db.package_migrations.operations.base import (
    _AlterRowOperation,
    _CreateRowOperation,
    _DeleteRowOperation,
)


class CreateEdge(_CreateRowOperation):
    model = models.Edge
    verbose_name = "edge"


class AlterEdge(_AlterRowOperation):
    model = models.Edge
    verbose_name = "edge"


class DeleteEdge(_DeleteRowOperation):
    model = models.Edge
    verbose_name = "edge"
