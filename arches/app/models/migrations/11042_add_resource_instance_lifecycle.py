import uuid
from django.db import migrations, models


def create_default_resource_instance_lifecycle(apps, schema_editor):
    ResourceInstanceLifecycle = apps.get_model("models", "ResourceInstanceLifecycle")
    ResourceInstanceLifecycle.objects.create(
        id=uuid.UUID("7e3cce56-fbfb-4a4b-8e83-59b9f9e7cb75"),
        name="standard",
    )


def remove_default_resource_instance_lifecycle(apps, schema_editor):
    ResourceInstanceLifecycle = apps.get_model("models", "ResourceInstanceLifecycle")
    resource_instance_lifecycle = ResourceInstanceLifecycle.objects.get(
        id="7e3cce56-fbfb-4a4b-8e83-59b9f9e7cb75"
    )
    resource_instance_lifecycle.delete()


def create_default_resource_instance_lifecycle_states(apps, schema_editor):
    ResourceInstanceLifecycleState = apps.get_model(
        "models", "ResourceInstanceLifecycleState"
    )
    draft_state = ResourceInstanceLifecycleState.objects.create(
        id=uuid.UUID("9375c9a7-dad2-4f14-a5c1-d7e329fdde4f"),
        name="draft",
        resource_instance_lifecycle_id=uuid.UUID(
            "7e3cce56-fbfb-4a4b-8e83-59b9f9e7cb75"
        ),
        is_initial_state=True,
        can_delete_resource_instances=True,
        can_edit_resource_instances=False,
    )
    active_state = ResourceInstanceLifecycleState.objects.create(
        id=uuid.UUID("f75bb034-36e3-4ab4-8167-f520cf0b4c58"),
        name="active",
        resource_instance_lifecycle_id=uuid.UUID(
            "7e3cce56-fbfb-4a4b-8e83-59b9f9e7cb75"
        ),
        is_initial_state=False,
        can_delete_resource_instances=False,
        can_edit_resource_instances=False,
    )
    retired_state = ResourceInstanceLifecycleState.objects.create(
        id=uuid.UUID("d95d9c0e-0e2c-4450-93a3-d788b91abcc8"),
        name="retired",
        resource_instance_lifecycle_id=uuid.UUID(
            "7e3cce56-fbfb-4a4b-8e83-59b9f9e7cb75"
        ),
        is_initial_state=False,
        can_delete_resource_instances=False,
        can_edit_resource_instances=False,
    )

    draft_state.next_resource_instance_lifecycle_states.add(active_state)
    active_state.next_resource_instance_lifecycle_states.add(retired_state)

    active_state.previous_resource_instance_lifecycle_states.add(draft_state)
    retired_state.previous_resource_instance_lifecycle_states.add(active_state)


def remove_default_resource_instance_lifecycle_states(apps, schema_editor):
    ResourceInstanceLifecycleState = apps.get_model(
        "models", "ResourceInstanceLifecycleState"
    )

    draft_state = ResourceInstanceLifecycleState.objects.get(
        id="9375c9a7-dad2-4f14-a5c1-d7e329fdde4f"
    )
    active_state = ResourceInstanceLifecycleState.objects.get(
        id="f75bb034-36e3-4ab4-8167-f520cf0b4c58"
    )
    retired_state = ResourceInstanceLifecycleState.objects.get(
        id="d95d9c0e-0e2c-4450-93a3-d788b91abcc8"
    )

    draft_state.delete()
    active_state.delete()
    retired_state.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("models", "9525_add_published_graph_edits"),
    ]

    operations = [
        migrations.CreateModel(
            name="ResourceInstanceLifecycle",
            fields=[
                ("id", models.UUIDField(primary_key=True, serialize=False)),
                ("name", models.TextField()),
            ],
            options={
                "db_table": "resource_instance_lifecycles",
                "managed": True,
            },
        ),
        migrations.CreateModel(
            name="ResourceInstanceLifecycleState",
            fields=[
                ("id", models.UUIDField(primary_key=True, serialize=False)),
                ("name", models.TextField()),
                ("is_initial_state", models.BooleanField(default=False)),
                ("can_edit_resource_instances", models.BooleanField(default=False)),
                ("can_delete_resource_instances", models.BooleanField(default=False)),
                (
                    "resource_instance_lifecycle",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="resource_instance_lifecycle_states",
                        to="models.ResourceInstanceLifecycle",
                    ),
                ),
            ],
            options={
                "db_table": "resource_instance_lifecycle_states",
                "managed": True,
            },
        ),
        migrations.CreateModel(
            name="ResourceInstanceLifecycleStateXResourceInstanceLifecycleState",
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
                    "resource_instance_lifecycle_state_from",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="previous_resource_instance_lifecycle_state",
                        to="models.ResourceInstanceLifecycleState",
                    ),
                ),
                (
                    "resource_instance_lifecycle_state_to",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="next_resource_instance_lifecycle_state",
                        to="models.ResourceInstanceLifecycleState",
                    ),
                ),
            ],
            options={
                "db_table": "resource_instance_lifecycle_states_xref",
                "managed": True,
            },
        ),
        migrations.AddField(
            model_name="resourceinstancelifecyclestate",
            name="previous_resource_instance_lifecycle_states",
            field=models.ManyToManyField(
                related_name="next_lifecycle_states",
                through="models.ResourceInstanceLifecycleStateXResourceInstanceLifecycleState",
                through_fields=(
                    "resource_instance_lifecycle_state_to",
                    "resource_instance_lifecycle_state_from",
                ),
                to="models.ResourceInstanceLifecycleState",
            ),
        ),
        migrations.AddField(
            model_name="resourceinstancelifecyclestate",
            name="next_resource_instance_lifecycle_states",
            field=models.ManyToManyField(
                related_name="previous_lifecycle_states",
                through="models.ResourceInstanceLifecycleStateXResourceInstanceLifecycleState",
                through_fields=(
                    "resource_instance_lifecycle_state_from",
                    "resource_instance_lifecycle_state_to",
                ),
                to="models.ResourceInstanceLifecycleState",
            ),
        ),
        migrations.RunPython(
            create_default_resource_instance_lifecycle,
            remove_default_resource_instance_lifecycle,
        ),
        migrations.RunPython(
            create_default_resource_instance_lifecycle_states,
            remove_default_resource_instance_lifecycle_states,
        ),
        migrations.AddField(
            model_name="graphmodel",
            name="resource_instance_lifecycle",
            field=models.ForeignKey(
                on_delete=models.PROTECT,
                related_name="graphs",
                to="models.ResourceInstanceLifecycle",
            ),
        ),
        migrations.AddField(
            model_name="resourceinstance",
            name="resource_instance_lifecycle_state",
            field=models.ForeignKey(
                default=uuid.UUID("f75bb034-36e3-4ab4-8167-f520cf0b4c58"),
                on_delete=models.deletion.PROTECT,
                related_name="resource_instances",
                to="models.ResourceInstanceLifecycleState",
            ),
            preserve_default=False,
        ),
    ]
