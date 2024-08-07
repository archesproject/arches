# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-01-25 16:00


from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("models", "4357_updates_default_resource_instance_download"),
    ]

    operations = [
        migrations.CreateModel(
            name="MobileSyncLog",
            fields=[
                (
                    "logid",
                    models.UUIDField(
                        default=uuid.uuid1, primary_key=True, serialize=False
                    ),
                ),
                ("started", models.DateTimeField(auto_now_add=True, null=True)),
                ("finished", models.DateTimeField(auto_now=True, null=True)),
                ("tilescreated", models.IntegerField(default=0, null=True)),
                ("tilesupdated", models.IntegerField(default=0, null=True)),
                ("tilesdeleted", models.IntegerField(default=0, null=True)),
                ("resourcescreated", models.IntegerField(default=0, null=True)),
                ("note", models.TextField(blank=True, null=True)),
                (
                    "survey",
                    models.ForeignKey(
                        on_delete=models.SET_NULL,
                        related_name="surveyid",
                        to="models.MobileSurveyModel",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=models.SET_NULL,
                        related_name="syncedby",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "mobile_sync_log",
                "managed": True,
            },
        )
    ]
