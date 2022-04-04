import datetime
import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.contrib.postgres.fields import JSONField

class Migration(migrations.Migration):

    dependencies = [
        ("models", "7783_make_settings_active"),
    ]

    def forwards_add_graph_column_data(apps, schema_editor):
        GraphPublication = apps.get_model("models", "GraphPublication")
        GraphModel = apps.get_model("models", "GraphModel")

        for graph in GraphModel.objects.all():
            graph_publications = GraphPublication.objects.filter(graph=graph)  # filtering for silent failure

            if len(graph_publications):
                graph.publication = graph_publications[0]
                graph.save()

    def reverse_add_graph_column_data(apps, schema_editor):
        GraphModel = apps.get_model("models", "GraphModel")

        for graph in GraphModel.objects.all():
            if graph.publication:
                graph.isactive = True

            graph.publication = None
            graph.save()

    operations = [
        migrations.CreateModel(
            name="GraphPublication",
            fields=[
                ("publicationid", models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
                ("notes", models.TextField(blank=True, null=True)),
                ("graph", models.ForeignKey(db_column="graphid", on_delete=models.deletion.CASCADE, to="models.GraphModel")),
                (
                    "user",
                    models.ForeignKey(
                        null=True, db_column="userid", on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
                ("published_time", models.DateTimeField(default=datetime.datetime.now())),
            ],
            options={
                "db_table": "graph_publications",
                "managed": True,
            },
        ),
        migrations.AddField(
            model_name="graphmodel",
            name="publication",
            field=models.ForeignKey(to="models.GraphPublication", db_column="publicationid", null=True, on_delete=models.SET_NULL),
        ),
        migrations.AddField(
            model_name="graphpublication",
            name="serialized_graph",
            field=JSONField(blank=True, db_column="serialized_graph", null=True),
        ),
        migrations.AlterField(
            model_name="graphmodel",
            name="isactive",
            field=models.BooleanField(verbose_name="isactive", default=False),
        ),
        migrations.RemoveField(
            model_name="graphmodel",
            name="isactive",
        ),
        migrations.AddField(
            model_name="resourceinstance",
            name="graph_publication",
            field=models.ForeignKey(db_column="graphpublicationid", null=True, on_delete=models.PROTECT, to="models.GraphPublication"),
        ),
        migrations.RunPython(forwards_add_graph_column_data, reverse_add_graph_column_data),
    ]
