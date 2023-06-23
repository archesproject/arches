import json
import uuid

from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.operations.base import Operation
from django.db.migrations.executor import MigrationExecutor

from arches.app.models import models
from arches.app.models.graph import Graph
from arches.app.models.system_settings import settings


class ArchesDataMigration(Operation):
    # If this is False, it means that this operation will be ignored by
    # sqlmigrate; if true, it will be run and the SQL collected for its output.
    reduces_to_sql = False

    # If this is False, Django will refuse to reverse past this operation.
    reversible = False

    @staticmethod
    def get_current_migration_name(app_label):
        connection = connections[DEFAULT_DB_ALIAS]
        connection.prepare_database()
        executor = MigrationExecutor(connection)
        targets = executor.loader.graph.leaf_nodes()

        migration = None
        for target in targets:
            if target[0] == app_label:
                migration = target[1]

        return migration

    def __init__(self, arg1, arg2):
        # Operations are usually instantiated with arguments in migration
        # files. Store the values of them on self for later use.
        pass

    def state_forwards(self, app_label, state):
        # The Operation should take the 'state' parameter (an instance of
        # django.db.migrations.state.ProjectState) and mutate it to match
        # any schema changes that have occurred.
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        # The Operation should use schema_editor to apply any changes it
        # wants to make to the database.
        pass

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        # If reversible is True, this is called when the operation is reversed.
        pass

    def describe(self):
        # This is used to describe what the operation does in console output.
        return "Custom Operation"

    @property
    def migration_name_fragment(self):
        # Optional. A filename part suitable for automatically naming a
        # migration containing this operation, or None if not applicable.
        return "custom_operation_%s_%s" % (self.arg1, self.arg2)
    

class UpdateResourceInstancesPublicationId(ArchesDataMigration):
    # If this is False, it means that this operation will be ignored by
    # sqlmigrate; if true, it will be run and the SQL collected for its output.
    reduces_to_sql = False

    # If this is False, Django will refuse to reverse past this operation.
    reversible = True

    def __init__(self, current_publication_id, updated_publication_id):
        self.current_publication_id = current_publication_id
        self.updated_publication_id = updated_publication_id

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        # The Operation should use schema_editor to apply any changes it
        # wants to make to the database.
        current_migration_name = self.get_current_migration_name(app_label=app_label)
        operation_name = self.__class__.__name__

        data_migration = models.DataMigration.objects.create(
            name=current_migration_name,
            app=app_label,
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
        current_migration_name = self.get_current_migration_name(app_label=app_label)
        operation_name = self.__class__.__name__

        data_migration = models.DataMigration.objects.filter(
            name=current_migration_name, 
            app=app_label,
            operation=operation_name
        ).last()

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
    

class AddNodeToTileData(ArchesDataMigration):
    # If this is False, it means that this operation will be ignored by
    # sqlmigrate; if true, it will be run and the SQL collected for its output.
    reduces_to_sql = False

    # If this is False, Django will refuse to reverse past this operation.
    reversible = True

    def __init__(self, publication_id, nodegroup_id, node_id, value):
        self.publication_id = publication_id
        self.nodegroup_id = nodegroup_id
        self.node_id = node_id
        self.value = value

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        # The Operation should use schema_editor to apply any changes it
        # wants to make to the database.
        current_migration_name = self.get_current_migration_name(app_label=app_label)
        operation_name = self.__class__.__name__

        data_migration = models.DataMigration.objects.create(
            name=current_migration_name,
            app=app_label,
            operation = operation_name,
        )
        data_migration.save()

        schema_editor.execute(
            """
            UPDATE tiles
            SET tiledata = jsonb_set(tiledata, '{%s}', jsonb_build_object('en', jsonb_build_object('value', '%s', 'direction', 'ltr')))
            WHERE nodegroupid = '%s'
            AND resourceinstanceid = ANY(                
                SELECT resourceinstanceid 
                FROM resource_instances 
                WHERE graphpublicationid = '%s'
            )
            AND NOT tiledata @> jsonb_build_array('%s')
            """ % (self.node_id, self.value, self.nodegroup_id, self.publication_id, self.node_id)
        )


    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        # If reversible is True, this is called when the operation is reversed.
        current_migration_name = self.get_current_migration_name(app_label=app_label)
        operation_name = self.__class__.__name__

        data_migration = models.DataMigration.objects.filter(
            name=current_migration_name, 
            app=app_label,
            operation=operation_name
        ).last()

        schema_editor.execute(
            """
            UPDATE tiles
            SET tiledata = tiledata - '%s'
            WHERE nodegroupid = '%s'
            AND resourceinstanceid = ANY(                
                SELECT resourceinstanceid 
                FROM resource_instances 
                WHERE graphpublicationid = '%s'
            )
            AND NOT tiledata @> jsonb_build_array('%s')
            """ % (self.node_id, self.nodegroup_id, self.publication_id, self.node_id)
        )

        data_migration.delete()

    def describe(self):
        # This is used to describe what the operation does in console output.
        return "Updates resources' publication_id from %s to %s" % (self.current_publication_id, self.updated_publication_id)
    

class UpdateGraphFromJSON(ArchesDataMigration):
    # If this is False, it means that this operation will be ignored by
    # sqlmigrate; if true, it will be run and the SQL collected for its output.
    reduces_to_sql = False

    # If this is False, Django will refuse to reverse past this operation.
    reversible = True

    def __init__(self, json_path):
        self.json_path = json_path

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        # The Operation should use schema_editor to apply any changes it
        # wants to make to the database.
        current_migration_name = self.get_current_migration_name(app_label=app_label)
        operation_name = self.__class__.__name__

        with open(self.json_path, 'r') as f:
            data = json.load(f)

        graph_data = data['graph'][0]
        graph = Graph.objects.get(pk=graph_data['graphid'])
        previous_graph_publication_id = graph.publication_id

        updated_graph = graph.restore_state_from_serialized_graph(graph_data)
        
        data_migration = models.DataMigration.objects.create(
            name=current_migration_name,
            app=app_label,
            operation = operation_name,
            metadata=json.dumps({
                'previous_publication_id': str(previous_graph_publication_id),
                'current_publication_id': str(updated_graph.publication_id)
            })
        )

        data_migration.save()

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        # If reversible is True, this is called when the operation is reversed.
        current_migration_name = self.get_current_migration_name(app_label=app_label)
        operation_name = self.__class__.__name__

        data_migration = models.DataMigration.objects.filter(
            name=current_migration_name, 
            app=app_label,
            operation=operation_name
        ).last()

        metadata = json.loads(data_migration.metadata)
        previous_publication_id = metadata['previous_publication_id']
        published_graph = models.PublishedGraph.objects.get(publication_id=previous_publication_id, language=settings.LANGUAGE_CODE)

        previous_graph = Graph.objects.get(pk=published_graph.serialized_graph['graphid'])
        previous_graph.restore_state_from_serialized_graph(published_graph.serialized_graph)

        data_migration.delete()

    def describe(self):
        # This is used to describe what the operation does in console output.
        return "Updates a graph from exported JSON"