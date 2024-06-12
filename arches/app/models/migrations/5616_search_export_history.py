# Generated by Django 2.2.6 on 2019-12-16 13:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("models", "5669_maplayer_searchonly"),
    ]

    operations = [
        migrations.CreateModel(
            name="SearchExportHistory",
            fields=[
                (
                    "searchexportid",
                    models.UUIDField(
                        default=uuid.uuid1, primary_key=True, serialize=False
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("numberofinstances", models.IntegerField()),
                ("exporttime", models.DateTimeField(auto_now_add=True)),
                ("url", models.TextField()),
            ],
            options={"db_table": "search_export_history", "managed": True},
        ),
    ]
