from django.db import migrations, models


def default_states():
    return {
        "active": {"can_delete": False, "initial_state": True},
        "retired": {"can_delete": True, "initial_state": False},
    }


def create_resource_instance_lifecycle_state(apps, schema_editor):
    GraphModel = apps.get_model("models", "GraphModel")
    ResourceInstanceLifecycle = apps.get_model("models", "ResourceInstanceLifecycle")

    for graph in GraphModel.objects.all():
        resource_instance_lifecycle = ResourceInstanceLifecycle.objects.create(
            graph=graph, states=default_states()
        )
        graph.resource_instance_lifecycle = resource_instance_lifecycle
        graph.save()


def remove_resource_instance_lifecycle_state(apps, schema_editor):
    GraphModel = apps.get_model("models", "GraphModel")
    ResourceInstanceLifecycle = apps.get_model("models", "ResourceInstanceLifecycle")

    for graph in GraphModel.objects.all():
        try:
            resource_instance_lifecycle = graph.resource_instance_lifecycle
            graph.resource_instance_lifecycle = None
            graph.save()
            resource_instance_lifecycle.delete()
        except ResourceInstanceLifecycle.DoesNotExist:
            continue


class Migration(migrations.Migration):

    dependencies = [
        ("models", "9525_add_published_graph_edits"),
    ]

    operations = [
        migrations.CreateModel(
            name="ResourceInstanceLifecycle",
            fields=[
                (
                    "graph",
                    models.OneToOneField(
                        on_delete=models.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to="models.GraphModel",
                    ),
                ),
                ("states", models.JSONField(default=default_states)),
            ],
            options={
                "db_table": "resource_instance_lifecycles",
                "managed": True,
            },
        ),
        migrations.AddField(
            model_name="graphmodel",
            name="resource_instance_lifecycle",
            field=models.ForeignKey(
                null=True,
                on_delete=models.CASCADE,
                to="models.ResourceInstanceLifecycle",
            ),
        ),
        migrations.AddField(
            model_name="resourceinstance",
            name="lifecycle_state",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.RunPython(
            create_resource_instance_lifecycle_state,
            remove_resource_instance_lifecycle_state,
        ),
    ]
