from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.recorder import MigrationRecorder
from django.db.migrations.operations.base import Operation
from django.db.migrations.executor import MigrationExecutor

from arches.app.models import models


class UpdatePublicationId(Operation):
    # If this is False, it means that this operation will be ignored by
    # sqlmigrate; if true, it will be run and the SQL collected for its output.
    reduces_to_sql = False

    # If this is False, Django will refuse to reverse past this operation.
    reversible = True

    @staticmethod
    def get_current_migration():
        connection = connections[DEFAULT_DB_ALIAS]
        connection.prepare_database()
        executor = MigrationExecutor(connection)
        targets = executor.loader.graph.leaf_nodes()
        migration_list = executor.migration_plan(targets)
        
        current_migration = None
        if len(migration_list):
            current_migration = migration_list[0][0]

        return current_migration

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
        current_migration = self.get_current_migration()
        operation_name = self.__class__.__name__

        data_migration = models.DataMigration.objects.create(
            name=current_migration.name,
            operation = operation_name,
            resource_instance_ids=[ 
                resource_instance_id 
                for resource_instance_id 
                in models.ResourceInstance.objects.filter(graph_publication_id=self.current_publication_id).values_list('resourceinstanceid', flat=True)
            ]
        )
        data_migration.save()

        schema_editor.execute(
            "UPDATE resource_instances SET graphpublicationid = '%s' WHERE graphpublicationid = '%s'" % (self.updated_publication_id, self.current_publication_id)
        )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        # If reversible is True, this is called when the operation is reversed.
        most_recent_migration = MigrationRecorder.Migration.objects.latest('id')
        operation_name = self.__class__.__name__

        data_migration = models.DataMigration.objects.filter(name=most_recent_migration.name, operation=operation_name).last()

        schema_editor.execute(
            """
            UPDATE resource_instances 
            SET graphpublicationid = '%s' 
            WHERE graphpublicationid = '%s'
            AND resourceinstanceid = ANY(ARRAY%s::uuid[])
            """ % (self.current_publication_id, self.updated_publication_id, data_migration.resource_instance_ids)
        )

        data_migration.delete()

    def describe(self):
        # This is used to describe what the operation does in console output.
        return "Updates resources' publication_id from %s to %s" % (self.current_publication_id, self.updated_publication_id)