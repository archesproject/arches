from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('models', '9979_update_stage_for_bulk_edit'),
    ]

    operations = [
        migrations.RunSQL(
            sql = """
            INSERT INTO d_data_types(
                datatype, 
                iconclass, 
                modulename,
                classname, 
                defaultconfig, 
                configcomponent,
                configname, 
                isgeometric, 
                defaultwidget,
                issearchable
            ) VALUES (
                'string-nonlocalized',
                'fa fa-file-code-o',
                'datatypes.py',
                'StringNonLocalizedDataType',
                null,
                'views/components/datatypes/string-nonlocalized',
                'string-nonlocalized-datatype-config',
                FALSE,
                '46ef064b-2611-4708-9f52-60136bd8a65b',
                TRUE
            );
            INSERT INTO widgets(
                widgetid,
                name,
                component,
                datatype,
                defaultconfig
            ) VALUES (
                '46ef064b-2611-4708-9f52-60136bd8a65b',
                'text-nonlocalized-widget',
                'views/components/widgets/text-nonlocalized',
                'string-nonlocalized',
                '{
                    "width": "100%",
                    "maxLength": null,
                    "uneditable": false,
                    "placeholder": "Enter text",
                    "defaultValue": ""
                }'
            );
            """,
            reverse_sql = """
            DELETE FROM d_data_types
                WHERE datatype = 'string-nonlocalized';
            DELETE from widgets
                WHERE widgetid = '46ef064b-2611-4708-9f52-60136bd8a65b';
            """
            ),
        ]