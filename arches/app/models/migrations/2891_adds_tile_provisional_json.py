# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-02-01 15:20


import django.contrib.postgres.fields.jsonb
from django.db import migrations

# import arches.app.utils.index_database as index_database


class Migration(migrations.Migration):

    dependencies = [
        ("models", "2891_tile_qa_schema"),
    ]

    operations = [
        migrations.AddField(
            model_name="tilemodel",
            name="provisionaledits",
            field=django.contrib.postgres.fields.jsonb.JSONField(
                blank=True, db_column="provisionaledits", null=True
            ),
        ),
    ]
