# Generated by Django 2.2.6 on 2019-10-18 15:57

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("models", "5394_postgis_mvt_api"),
    ]

    operations = [
        migrations.DeleteModel(
            name="TileserverLayer",
        ),
    ]
