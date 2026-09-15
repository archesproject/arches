"""Node operations.

Structural only: creating a node does not put a key in any tile, and deleting
one does not remove it. That is what the data operations are for, and keeping
them separate is what lets a chunked backfill run in its own non-atomic
migration.
"""

from arches.app.models import models
from arches.db.package_migrations.operations.base import PackageOperation


class CreateNode(PackageOperation):
    reversible = True

    def __init__(
        self,
        graphid,
        nodeid,
        name,
        datatype,
        alias,
        nodegroup_id=None,
        description=None,
        istopnode=False,
        isrequired=False,
        issearchable=True,
        exportable=False,
        sortorder=0,
        ontologyclass=None,
        config=None,
        hascustomalias=True,
    ):
        # Attribute names must match parameter names -- deconstruct() reads them
        # back off self, and OperationWriter silently drops any kwarg that is not
        # an __init__ parameter. Nothing is normalized here for the same reason.
        self.graphid = graphid
        self.nodeid = nodeid
        self.name = name
        self.datatype = datatype
        self.alias = alias
        self.nodegroup_id = nodegroup_id
        self.description = description
        self.istopnode = istopnode
        self.isrequired = isrequired
        self.issearchable = issearchable
        self.exportable = exportable
        self.sortorder = sortorder
        self.ontologyclass = ontologyclass
        self.config = config
        # hascustomalias=True keeps Node.clean() from re-deriving the alias from
        # the active-language name via the __arches_slugify stored procedure,
        # which would make the value depend on the target install.
        self.hascustomalias = hascustomalias

    def state_forwards(self, app_label, state):
        state.graphs[str(self.graphid)]["nodes"][str(self.nodeid)] = {
            "nodeid": str(self.nodeid),
            "name": self.name,
            "datatype": self.datatype,
            "alias": self.alias,
            "nodegroup_id": (
                str(self.nodegroup_id) if self.nodegroup_id is not None else None
            ),
            "description": self.description,
            "istopnode": self.istopnode,
            "isrequired": self.isrequired,
            "issearchable": self.issearchable,
            "exportable": self.exportable,
            "sortorder": self.sortorder,
            "ontologyclass": self.ontologyclass,
            "config": self.config,
            "hascustomalias": self.hascustomalias,
        }

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        self.qs(models.Node, schema_editor).create(
            nodeid=self.nodeid,
            graph_id=self.graphid,
            nodegroup_id=self.nodegroup_id,
            name=self.name,
            description=self.description,
            datatype=self.datatype,
            alias=self.alias,
            hascustomalias=self.hascustomalias,
            istopnode=self.istopnode,
            isrequired=self.isrequired,
            issearchable=self.issearchable,
            exportable=self.exportable,
            sortorder=self.sortorder,
            ontologyclass=self.ontologyclass,
            config=self.config,
        )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        self.qs(models.Node, schema_editor).filter(pk=self.nodeid).delete()

    def describe(self):
        return "Create node %s (%s) on graph %s" % (
            self.alias,
            self.datatype,
            self.graphid,
        )

    @property
    def migration_name_fragment(self):
        return "node_%s" % self.alias


class DeleteNode(PackageOperation):
    # Reversible: unapply() phase 1 replays state forwards, so to_state still
    # holds the node's full definition for database_backwards to recreate from.
    reversible = True

    def __init__(self, graphid, nodeid):
        self.graphid = graphid
        self.nodeid = nodeid

    def state_forwards(self, app_label, state):
        del state.graphs[str(self.graphid)]["nodes"][str(self.nodeid)]

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        # ORM delete, not raw SQL: CardXNodeXWidget.node and ConstraintXNode.node
        # are CASCADE at the ORM level only (the DB FK is NO ACTION), so a raw
        # DELETE FROM nodes would fail on the FK.
        self.qs(models.Node, schema_editor).filter(pk=self.nodeid).delete()

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        node = to_state.graphs[str(self.graphid)]["nodes"][str(self.nodeid)]
        self.qs(models.Node, schema_editor).create(
            nodeid=node["nodeid"],
            graph_id=self.graphid,
            nodegroup_id=node.get("nodegroup_id"),
            name=node["name"],
            description=node.get("description"),
            datatype=node["datatype"],
            alias=node["alias"],
            hascustomalias=node.get("hascustomalias", True),
            istopnode=node.get("istopnode", False),
            isrequired=node.get("isrequired", False),
            issearchable=node.get("issearchable", True),
            exportable=node.get("exportable", False),
            sortorder=node.get("sortorder", 0),
            ontologyclass=node.get("ontologyclass"),
            config=node.get("config"),
        )

    def describe(self):
        return "Delete node %s from graph %s" % (self.nodeid, self.graphid)

    @property
    def migration_name_fragment(self):
        return "delete_node_%s" % str(self.nodeid).replace("-", "")[:8]
