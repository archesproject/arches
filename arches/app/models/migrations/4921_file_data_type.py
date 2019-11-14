from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "4989_related_resources_map_card"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            UPDATE d_data_types
            SET configcomponent = 'views/components/datatypes/file-list',
            configname = 'file-list-datatype-config',
            defaultconfig = '{"maxFiles":1,"activateMax":false,"maxFileSize":null}'
            WHERE defaultwidget = '10000000-0000-0000-0000-000000000019';
            """,
            reverse_sql="""
            UPDATE d_data_types
            SET configcomponent = '',
            configname = '',
            defaultconfig = null
            WHERE defaultwidget = '10000000-0000-0000-0000-000000000019';
            """,
        ),
    ]
