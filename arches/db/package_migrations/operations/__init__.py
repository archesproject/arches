"""Package migration operations.

Public API: generated migration files import these by dotted path and ship inside
third-party wheels. Constructor signatures are additive-only -- new parameters
must have defaults, and removing one requires a two-release deprecation.
"""

from arches.db.package_migrations.operations.base import PackageOperation
from arches.db.package_migrations.operations.card import (
    AlterCard,
    CreateCard,
    DeleteCard,
)
from arches.db.package_migrations.operations.data import (
    BackfillNodeData,
    CoerceNodeData,
    DeleteTilesForNodeGroup,
    RemoveNodeData,
)
from arches.db.package_migrations.operations.edge import (
    AlterEdge,
    CreateEdge,
    DeleteEdge,
)
from arches.db.package_migrations.operations.graph import AlterGraph, CreateGraph
from arches.db.package_migrations.operations.node import (
    AlterNode,
    CreateNode,
    DeleteNode,
)
from arches.db.package_migrations.operations.nodegroup import (
    AlterNodeGroup,
    CreateNodeGroup,
    DeleteNodeGroup,
)
from arches.db.package_migrations.operations.publish import (
    PublishGraph,
    RefreshDraftGraph,
    RepointResourceInstances,
)
from arches.db.package_migrations.operations.special import RunPackagePython
from arches.db.package_migrations.operations.widget import (
    AlterCardXNodeXWidget,
    CreateCardXNodeXWidget,
    DeleteCardXNodeXWidget,
)

__all__ = [
    "PackageOperation",
    "CreateGraph",
    "AlterGraph",
    "CreateNodeGroup",
    "AlterNodeGroup",
    "DeleteNodeGroup",
    "CreateNode",
    "AlterNode",
    "DeleteNode",
    "CreateEdge",
    "AlterEdge",
    "DeleteEdge",
    "CreateCard",
    "AlterCard",
    "DeleteCard",
    "CreateCardXNodeXWidget",
    "AlterCardXNodeXWidget",
    "DeleteCardXNodeXWidget",
    "BackfillNodeData",
    "RemoveNodeData",
    "CoerceNodeData",
    "DeleteTilesForNodeGroup",
    "PublishGraph",
    "RepointResourceInstances",
    "RefreshDraftGraph",
    "RunPackagePython",
]
