from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('models', '10006_fix_escape_chars_breaking_bulk_edit'),
    ]

    operations = [
        migrations.RunSQL(
            """
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
            INSERT INTO widgets(
                widgetid,
                name,
                component,
                datatype,
                defaultconfig
            ) VALUES (
                'a952163c-0bae-4ac8-949b-12dd2379fe6d',
                'rich-text-nonlocalized-widget',
                'views/components/widgets/rich-text-nonlocalized',
                'string-nonlocalized',
                '{}'
            );
            """
            # """
            # DELETE FROM d_data_types
            #     WHERE datatype = 'string-nonlocalized';
            # DELETE from widgets
            #     WHERE widgetid = '46ef064b-2611-4708-9f52-60136bd8a65b';
            # DELETE from widgets
            #     WHERE widgetid = 'a952163c-0bae-4ac8-949b-12dd2379fe6d';
            # """
            ),
        ]