# Generated by Django 2.2.9 on 2020-04-07 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "5935_2way_sync"),
    ]

    operations = [
        migrations.CreateModel(
            name="IIIFManifest",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("label", models.TextField()),
                ("url", models.TextField()),
                ("description", models.TextField(blank=True, null=True)),
            ],
            options={
                "db_table": "iiif_manifests",
                "managed": True,
            },
        ),
    ]
