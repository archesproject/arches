from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '7131_update_annotations_view'),
    ]

    operations = [
        migrations.RunSQL("""
            UPDATE d_data_types
            SET defaultconfig = defaultconfig || '{"searchString": "", "searchDsl": ""}'::jsonb
            WHERE datatype = 'resource-instance' OR datatype = 'resource-instance-list';
            UPDATE nodes
            SET config = config || '{"searchString": "", "searchDsl": ""}'::jsonb
            WHERE datatype = 'resource-instance' OR datatype = 'resource-instance-list';
        ""","""
            UPDATE nodes
            SET config = config - 'searchString' - 'searchDsl'
            WHERE datatype = 'resource-instance' OR datatype = 'resource-instance-list';
            UPDATE d_data_types
            SET defaultconfig = defaultconfig - 'searchString' - 'searchDsl'
            WHERE datatype = 'resource-instance' OR datatype = 'resource-instance-list';
        """)
    ]
