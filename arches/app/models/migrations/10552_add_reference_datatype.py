from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "10541_controlled_list_manager"),
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
                'reference',
                'fa fa-list',
                'datatypes.py',
                'ReferenceDataType',
                'views/components/datatypes/reference',
                {"controlledList": null, "multiValue": false},
                reference-datatype-config,
                FALSE,
                '19e56148-82b8-47eb-b66e-f6243639a1a8',
                TRUE
            );

            INSERT INTO widgets(
                widgetid,
                name,
                component,
                datatype,
                defaultconfig
            ) VALUES (
                '19e56148-82b8-47eb-b66e-f6243639a1a8',
                'reference-select-widget',
                'views/components/widgets/reference-select',
                '{"i18n_properties": ["placeholder"]}',
                'reference'
            );

            """,
            reverse_sql="""
            DELETE FROM widgets WHERE widgetid = '19e56148-82b8-47eb-b66e-f6243639a1a8';
            DELETE FROM d_data_types WHERE datatype = 'reference';
            """,
        ),
    ]
