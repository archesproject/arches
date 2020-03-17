from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "4751_adds_photo_gallery_card"),
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
                'annotation',
                'fa fa-image',
                'datatypes.py',
                'AnnotationDataType',
                NULL,
                NULL,
                NULL,
                FALSE,
                'aae743b8-4c48-11ea-988b-2bc775672c81',
                FALSE
            );

            INSERT INTO widgets(
                widgetid,
                name,
                component,
                datatype,
                defaultconfig
            ) VALUES (
                'aae743b8-4c48-11ea-988b-2bc775672c81',
                'iiif-widget',
                'views/components/widgets/iiif',
                'annotation',
                '{
                    "defaultManifest": ""
                }'
            );

            INSERT INTO card_components(
                componentid,
                name,
                description,
                component,
                componentname,
                defaultconfig
            ) VALUES (
                '2ed3f508-4e8e-11ea-b975-5b976cab10db',
                'IIIF Card',
                '',
                'views/components/cards/iiif-card',
                'iiif-card',
                '{
                    "defaultManifest": ""
                }'
            );
            """,
            reverse_sql="""
            DELETE FROM card_components WHERE componentid = '2ed3f508-4e8e-11ea-b975-5b976cab10db';
            DELETE FROM widgets WHERE widgetid = 'aae743b8-4c48-11ea-988b-2bc775672c81';
            DELETE FROM d_data_types WHERE datatype = 'annotation';
            """,
        ),
    ]
