from django.conf import settings
from django.db import migrations, models
from arches.app.models.graph import Graph
from arches.app.utils.betterJSONSerializer import JSONSerializer


class Migration(migrations.Migration):

    dependencies = [
        ("models", "7783_add_graph_publications"),
    ]

    def forwards_add_serialized_graph_column_data(apps, schema_editor):
        GraphModel = apps.get_model("models", "GraphModel")

        for graph in GraphModel.objects.all():
            if graph.publication:
                arches_graph = Graph.objects.get(pk=graph.pk)
                graph.publication.serialized_graph = JSONSerializer().serialize(arches_graph.serialize(force_recalculation=True))

                graph.publication.save()

    def reverse_add_serialized_graph_column_data(apps, schema_editor):
        GraphPublication = apps.get_model("models", "GraphPublication")

        for graph_publication in GraphPublication.objects.all():
            graph_publication.serialized_graph = ""
            graph_publication.save()

    operations = [
        migrations.AddField(
            model_name="graphpublication",
            name="serialized_graph",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.RunPython(forwards_add_serialized_graph_column_data, reverse_add_serialized_graph_column_data),
        migrations.AlterField(
            model_name="graphmodel",
            name="isactive",
            field=models.BooleanField(verbose_name="isactive", default=False),
        ),
        migrations.RemoveField(
            model_name="graphmodel",
            name="isactive",
        ),
    ]
