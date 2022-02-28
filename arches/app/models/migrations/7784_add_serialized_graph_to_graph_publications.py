from django.conf import settings
from django.db import migrations, models
from arches.app.models.graph import Graph
from arches.app.models.models import ResourceInstance
from arches.app.utils.betterJSONSerializer import JSONSerializer
from django.contrib.postgres.fields import JSONField


class Migration(migrations.Migration):

    dependencies = [
        ("models", "7783_add_graph_publications"),
    ]

    def forwards_add_serialized_graph_column_data(apps, schema_editor):
        for graph in Graph.objects.all():
            if graph.publication:
                graph.publication.serialized_graph = JSONSerializer().serialize(graph, force_recalculation=True)
                graph.publication.save()

    def reverse_add_serialized_graph_column_data(apps, schema_editor):
        GraphPublication = apps.get_model("models", "GraphPublication")

        for graph_publication in GraphPublication.objects.all():
            graph_publication.serialized_graph = ""
            graph_publication.save()

    def forwards_add_resource_publications(apps, schema_editor):
        inactive_graphs = []
        for resource in ResourceInstance.objects.all():
            if(resource.graph.publication_id is not None):
                resource.graph_publication = resource.graph.publication
                resource.save()
            else:
                inactive_graphs = inactive_graphs + [resource.graph.name]
        
        if(len(inactive_graphs) > 0):
            raise Exception("All resource instances must have their associated graph set to active before migration.  The following inactive graphs have resource instances: {} ".format(", ".join(inactive_graphs)))

    def reverse_add_resource_publications(apps, schema):
        pass

    operations = [
        migrations.AddField(
            model_name="graphpublication",
            name="serialized_graph",
            field=JSONField(blank=True, db_column="serialized_graph", null=True),
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
        migrations.AddField(
            model_name='resourceinstance',
            name='graph_publication',
            field=models.ForeignKey(db_column='graphpublicationid', null=True, on_delete=models.PROTECT, to='models.GraphPublication'),
        ),
        migrations.RunPython(forwards_add_resource_publications, reverse_add_resource_publications),
        migrations.AlterField(
            model_name='resourceinstance',
            name='graph_publication',
            field=models.ForeignKey(db_column='graphpublicationid', null=False, on_delete=models.PROTECT, to='models.GraphPublication'),
        ),
    ]
