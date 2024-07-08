from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "10515_i18n_plugins"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
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
                'non-localized-string',
                'fa fa-file-code-o',
                'datatypes.py',
                'NonLocalizedStringDataType',
                null,
                'views/components/datatypes/non-localized-string',
                'non-localized-string-datatype-config',
                FALSE,
                '46ef064b-2611-4708-9f52-60136bd8a65b',
                TRUE
            ) ON CONFLICT DO NOTHING;
            INSERT INTO widgets(
                widgetid,
                name,
                component,
                datatype,
                defaultconfig
            ) VALUES (
                '46ef064b-2611-4708-9f52-60136bd8a65b',
                'non-localized-text-widget',
                'views/components/widgets/non-localized-text',
                'non-localized-string',
                '{
                    "width": "100%",
                    "maxLength": null,
                    "uneditable": false,
                    "placeholder": "Enter text",
                    "defaultValue": "",
                    "i18n_properties": [
                        "placeholder"
                    ]
                }'
            ) ON CONFLICT DO NOTHING;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
