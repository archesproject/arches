import uuid
from django.db.migrations.operations.base import Operation


class UpdatePublicationId(Operation):
    # If this is False, it means that this operation will be ignored by
    # sqlmigrate; if true, it will be run and the SQL collected for its output.
    reduces_to_sql = False

    # If this is False, Django will refuse to reverse past this operation.
    reversible = True

    def __init__(self, current_publication_id, updated_publication_id):
        self.current_publication_id = current_publication_id
        self.updated_publication_id = updated_publication_id

    def state_forwards(self, app_label, state):
        # The Operation should take the 'state' parameter (an instance of
        # django.db.migrations.state.ProjectState) and mutate it to match
        # any schema changes that have occurred.
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        # The Operation should use schema_editor to apply any changes it
        # wants to make to the database.
        schema_editor.execute("UPDATE resource_instances SET graphpublicationid = '%s' WHERE graphpublicationid = '%s'" % (self.updated_publication_id, self.current_publication_id))

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        # If reversible is True, this is called when the operation is reversed.
        schema_editor.execute("UPDATE resource_instances SET graphpublicationid = '%s' WHERE graphpublicationid = '%s'" % (self.current_publication_id, self.updated_publication_id))

    def describe(self):
        # This is used to describe what the operation does in console output.
        return "Updates resource publication_id from %s to %s" % (self.current_publication_id, self.updated_publication_id)