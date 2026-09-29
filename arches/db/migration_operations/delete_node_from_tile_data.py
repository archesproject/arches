import json

from django.db.models import JSONField
from django.db.models.expressions import RawSQL

from arches.app.models import models

from .base import ArchesPackageMigration


class DeleteNodeFromTileData(ArchesPackageMigration):
    reduces_to_sql = False
    reversible = True

    def __init__(self, publication_id, nodegroup_id, node_id, value):
        self.publication_id = publication_id
        self.nodegroup_id = nodegroup_id
        self.node_id = node_id
        self.value = value

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        models.TileModel.objects.filter(
            nodegroup_id=self.nodegroup_id,
            resourceinstance__graph_publication_id=self.publication_id,
        ).filter(
            data__has_key=self.node_id,
        ).update(
            data=RawSQL(
                "tiledata - %s",
                [self.node_id],
                output_field=JSONField(),
            )
        )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        models.TileModel.objects.filter(
            nodegroup_id=self.nodegroup_id,
            resourceinstance__graph_publication_id=self.publication_id,
        ).exclude(
            data__has_key=self.node_id,
        ).update(
            data=RawSQL(
                "jsonb_set(tiledata, ARRAY[%s], %s::jsonb)",
                [self.node_id, json.dumps(self.value)],
                output_field=JSONField(),
            )
        )

    def describe(self):
        return "Deletes node %s from tile data for nodegroup %s" % (
            self.node_id,
            self.nodegroup_id,
        )

    @staticmethod
    def as_migration_string(op: dict, pub_a_id: str) -> str:
        return "\n".join(
            [
                "        DeleteNodeFromTileData(",
                f"            publication_id={pub_a_id!r},",
                f"            nodegroup_id={op['nodegroup_id']!r},",
                f"            node_id={op['nodeid']!r},",
                f"            value=None,  # TODO: set default value for {op['alias']!r} ({op['datatype']!r})",
                "        ),",
            ]
        )
