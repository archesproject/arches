# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-02-07 15:17


from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("models", "4467_sync_log"),
    ]

    operations = [
        migrations.CreateModel(
            name="ResourceRevisionLog",
            fields=[
                (
                    "logid",
                    models.UUIDField(
                        default=uuid.uuid1, primary_key=True, serialize=False
                    ),
                ),
                ("resourceid", models.UUIDField(default=uuid.uuid1)),
                ("revisionid", models.TextField()),
                ("synctimestamp", models.DateTimeField(auto_now_add=True)),
                ("action", models.TextField(blank=True, null=True)),
                (
                    "survey",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mobile_survey_id",
                        to="models.MobileSurveyModel",
                    ),
                ),
            ],
            options={
                "db_table": "resource_revision_log",
                "managed": True,
            },
        ),
        migrations.CreateModel(
            name="TileRevisionLog",
            fields=[
                (
                    "logid",
                    models.UUIDField(
                        default=uuid.uuid1, primary_key=True, serialize=False
                    ),
                ),
                ("tileid", models.UUIDField(default=uuid.uuid1)),
                ("resourceid", models.UUIDField(default=uuid.uuid1)),
                ("revisionid", models.TextField()),
                ("synctimestamp", models.DateTimeField(auto_now_add=True)),
                ("action", models.TextField(blank=True, null=True)),
                (
                    "survey",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="survey_id",
                        to="models.MobileSurveyModel",
                    ),
                ),
            ],
            options={
                "db_table": "tile_revision_log",
                "managed": True,
            },
        ),
        migrations.AlterField(
            model_name="mobilesynclog",
            name="survey",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="surveyid",
                to="models.MobileSurveyModel",
            ),
        ),
        migrations.AlterField(
            model_name="mobilesynclog",
            name="user",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="tilerevisionlog",
            name="synclog",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="mobile_sync_log",
                to="models.MobileSyncLog",
            ),
        ),
        migrations.AddField(
            model_name="resourcerevisionlog",
            name="synclog",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sync_log",
                to="models.MobileSyncLog",
            ),
        ),
    ]
