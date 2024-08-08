import itertools

from django.db import migrations

from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.utils.index_database import index_resources_using_multiprocessing, index_resources_using_singleprocessing


class DataMigration(migrations.Migration):
    def __init__(self, name, app_label):
        super().__init__(name, app_label)

    def apply(self, project_state, schema_editor, collect_sql=False):    
        project_state = super().apply(project_state, schema_editor, collect_sql=collect_sql)

        data_migrations = models.DataMigration.objects.filter(
            name=self.name, 
            app=self.app_label,
        )
        resource_instance_ids = list(itertools.chain.from_iterable([data_migration.resource_instance_ids for data_migration in data_migrations]))
        index_resources_using_singleprocessing(resources=Resource.objects.filter(resourceinstanceid__in=resource_instance_ids))

        return project_state

    def unapply(self, project_state, schema_editor, collect_sql=False):
        project_state = super().unapply(project_state, schema_editor, collect_sql=collect_sql)
        
        data_migrations = models.DataMigration.objects.filter(
            name=self.name, 
            app=self.app_label,
        )
        resource_instance_ids = list(itertools.chain.from_iterable([data_migration.resource_instance_ids for data_migration in data_migrations]))
        index_resources_using_singleprocessing(resources=Resource.objects.filter(resourceinstanceid__in=resource_instance_ids))
        
        return project_state