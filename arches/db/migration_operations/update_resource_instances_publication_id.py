from .base import ArchesDataMigration


class UpdateResourceInstancesPublicationId(ArchesDataMigration):
    reduces_to_sql = False
    reversible = True

    def __init__(self, current_publication_id, updated_publication_id):
        self.current_publication_id = current_publication_id
        self.updated_publication_id = updated_publication_id

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute(
            "UPDATE resource_instances SET graphpublicationid = '%s' WHERE graphpublicationid = '%s'"
            % (self.updated_publication_id, self.current_publication_id)
        )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute(
            "UPDATE resource_instances SET graphpublicationid = '%s' WHERE graphpublicationid = '%s'"
            % (self.current_publication_id, self.updated_publication_id)
        )

    def describe(self):
        return "Updates resources' publication_id from %s to %s" % (
            self.current_publication_id,
            self.updated_publication_id,
        )

    @staticmethod
    def as_migration_string(pub_a_id: str, pub_b_id: str) -> str:
        return "\n".join(
            [
                "        UpdateResourceInstancesPublicationId(",
                f"            current_publication_id={pub_a_id!r},",
                f"            updated_publication_id={pub_b_id!r},",
                "        ),",
            ]
        )
