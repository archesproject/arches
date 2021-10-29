from django.conf import settings
from django.db import migrations, models
from arches.app.models.graph import Graph


class Migration(migrations.Migration):

    dependencies = [
        ("models", "7783_add_graph_publications"),
    ]

    def forwards_add_serialized_graph_column_data(apps, schema_editor):
        GraphPublication = apps.get_model("models", "GraphPublication")
        GraphModel = apps.get_model("models", "GraphModel")

        for graph in GraphModel.objects.all():
            if graph.publication:
                graph_publication = GraphPublication.objects.get(graph=graph)
                arches_graph = Graph.objects.get(pk=graph.pk)
                graph_publication.serialized_graph = arches_graph.serialize()
                graph_publication.save()

    def reverse_add_serialized_graph_column_data(apps, schema_editor):
        GraphPublication = apps.get_model("models", "GraphPublication")
        GraphModel = apps.get_model("models", "GraphModel")

        for graph in GraphModel.objects.all():
            if graph.publication:
                graph_publication = GraphPublication.objects.get(graph=graph)
                graph_publication.serialized_graph = None
                graph_publication.save()

    operations = [
        migrations.AddField(
            model_name="graphpublication",
            name="serialized_graph",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.RunPython(forwards_add_serialized_graph_column_data, reverse_add_serialized_graph_column_data),
    ]
