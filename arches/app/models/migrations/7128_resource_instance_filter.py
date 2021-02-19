from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '7043_sort_results'),
    ]

    operations = [
        migrations.RunSQL("""
            UPDATE d_data_types
            SET defaultconfig = defaultconfig || '{"searchString": ""}'::jsonb
            WHERE datatype = 'resource-instance' OR datatype = 'resource-instance-list';
            UPDATE nodes
            SET config = config || '{"searchString": ""}'::jsonb
            WHERE datatype = 'resource-instance' OR datatype = 'resource-instance-list';
        ""","""
            UPDATE nodes
            SET config = config - 'searchString'
            WHERE datatype = 'resource-instance' OR datatype = 'resource-instance-list';
            UPDATE d_data_types
            SET defaultconfig = defaultconfig - 'searchString'
            WHERE datatype = 'resource-instance' OR datatype = 'resource-instance-list';
        """)
    ]
