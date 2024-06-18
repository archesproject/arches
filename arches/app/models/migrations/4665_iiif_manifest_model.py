# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-023-05 14:40


from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("models", "4665_remove_disco_widgets"),
    ]

    operations = [
        migrations.DeleteModel(
            name="IIIFManifest",
        ),
        migrations.RunSQL(
            """
            DELETE FROM widgets WHERE datatype IN ('iiif-drawing', 'csv-chart-json');
            """,
            """
            INSERT INTO widgets(
                widgetid,
                name,
                component,
                datatype,
                defaultconfig)
            VALUES(
                '10000000-0000-0000-0000-000000000020',
                'csv-chart-widget',
                'views/components/widgets/csv-chart',
                'csv-chart-json',
                '{"acceptedFiles": "", "maxFilesize": "200"}'
            );

            INSERT INTO widgets(
                widgetid,
                name,
                component,
                datatype,
                defaultconfig)
            VALUES(
                '10000000-0000-0000-0000-000000000022',
                'iiif-widget',
                'views/components/widgets/iiif',
                'iiif-drawing',
                '{ "placeholder": "", "options": [], "nameLabel": "Name", "typeLabel": "Type"}'
            );
            """,
        ),
    ]
