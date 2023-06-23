from django.db import migrations

class DataMigration(migrations.Migration):
    def __init__(self, name, app_label):
        super().__init__(name, app_label)

    def apply(self, project_state, schema_editor, collect_sql=False):    
        foo = super().apply(project_state, schema_editor, collect_sql=collect_sql)
        print("!!!!" * 50)
        return foo

    def unapply(self, project_state, schema_editor, collect_sql=False):
        foo = super().apply(project_state, schema_editor, collect_sql=collect_sql)
        print("%%%%" * 50)
        return foo