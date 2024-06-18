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
        GraphXPublishedGraph = apps.get_model("models", "GraphXPublishedGraph")
        GraphModel = apps.get_model("models", "GraphModel")

        for graph in GraphModel.objects.all():
            graph_publications = GraphXPublishedGraph.objects.filter(
                graph=graph
            )  # filtering for silent failure

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
        # migrations.CreateModel(
        #     name="GraphXPublishedGraph",
        #     fields=[
        #         ("publicationid", models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
        #         ("notes", models.TextField(blank=True, null=True)),
        #         ("graph", models.ForeignKey(db_column="graphid", on_delete=models.deletion.CASCADE, to="models.GraphModel")),
        #         (
        #             "user",
        #             models.ForeignKey(
        #                 null=True, db_column="userid", on_delete=models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
        #             ),
        #         ),
        #         ("published_time", models.DateTimeField(default=datetime.datetime.now())),
        #     ],
        #     options={
        #         "db_table": "graphs_x_published_graphs",
        #         "managed": True,
        #     },
        # ),
        # migrations.CreateModel(
        #     name="PublishedGraph",
        #     fields=[
        #         ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        #         ("serialized_graph", django.contrib.postgres.fields.jsonb.JSONField(blank=True, db_column="serialized_graph", null=True)),
        #         ("language", models.ForeignKey(
        #                 blank=True,
        #                 null=True,
        #                 db_column="languageid",
        #                 to="models.Language",
        #                 to_field="code",
        #                 on_delete=models.CASCADE,
        #             ),
        #         ),
        #         (
        #             "publication",
        #             models.ForeignKey(db_column="publicationid", on_delete=models.deletion.CASCADE, to="models.GraphXPublishedGraph"),
        #         ),
        #     ],
        #     options={
        #         "db_table": "published_graphs",
        #         "managed": True,
        #     },
        # ),
        migrations.CreateModel(
            name="GraphXPublishedGraph",
            fields=[
                (
                    "publicationid",
                    models.UUIDField(
                        default=uuid.uuid1, primary_key=True, serialize=False
                    ),
                ),
                ("notes", models.TextField(blank=True, null=True)),
                ("published_time", models.DateTimeField(default=datetime.datetime.now)),
            ],
            options={
                "db_table": "graphs_x_published_graphs",
                "managed": True,
            },
        ),
        migrations.CreateModel(
            name="PublishedGraph",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "serialized_graph",
                    django.contrib.postgres.fields.jsonb.JSONField(
                        blank=True, db_column="serialized_graph", null=True
                    ),
                ),
            ],
            options={
                "db_table": "published_graphs",
                "managed": True,
            },
        ),
        migrations.AddField(
            model_name="publishedgraph",
            name="language",
            field=models.ForeignKey(
                blank=True,
                db_column="languageid",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="models.Language",
                to_field="code",
            ),
        ),
        migrations.AddField(
            model_name="publishedgraph",
            name="publication",
            field=models.ForeignKey(
                db_column="publicationid",
                on_delete=django.db.models.deletion.CASCADE,
                to="models.GraphXPublishedGraph",
            ),
        ),
        migrations.AddField(
            model_name="graphxpublishedgraph",
            name="graph",
            field=models.ForeignKey(
                db_column="graphid",
                on_delete=django.db.models.deletion.CASCADE,
                to="models.GraphModel",
            ),
        ),
        migrations.AddField(
            model_name="graphxpublishedgraph",
            name="user",
            field=models.ForeignKey(
                db_column="userid",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="graphmodel",
            name="publication",
            field=models.ForeignKey(
                to="models.GraphXPublishedGraph",
                db_column="publicationid",
                null=True,
                on_delete=models.SET_NULL,
            ),
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
            field=models.ForeignKey(
                db_column="graphpublicationid",
                null=True,
                on_delete=models.PROTECT,
                to="models.GraphXPublishedGraph",
            ),
        ),
        migrations.RunPython(
            forwards_add_graph_column_data, reverse_add_graph_column_data
        ),
    ]
