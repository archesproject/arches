# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-07-29 18:51


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("models", "4684_adds_config_to_tabbed_report"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tileserverlayer",
            name="map_layer",
            field=models.ForeignKey(
                db_column="map_layerid",
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="models.MapLayer",
            ),
        ),
        migrations.AlterField(
            model_name="tileserverlayer",
            name="map_source",
            field=models.ForeignKey(
                db_column="map_sourceid",
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="models.MapSource",
            ),
        ),
        migrations.AlterField(
            model_name="tileserverlayer",
            name="path",
            field=models.TextField(null=True, blank=True),
        ),
    ]
