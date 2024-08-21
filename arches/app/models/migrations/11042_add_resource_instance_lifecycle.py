import uuid
from django.db import migrations, models
from django.utils.translation import gettext as _


def create_perpetual_resource_instance_lifecycle(apps, schema_editor):
    ResourceInstanceLifecycle = apps.get_model("models", "ResourceInstanceLifecycle")
    ResourceInstanceLifecycle.objects.create(
        id=uuid.UUID("e9a8a2b0-63b5-47a3-bbc4-9c09c0e759b1"),
        name=_("Perpetual"),
    )


def remove_perpetual_resource_instance_lifecycle(apps, schema_editor):
    ResourceInstanceLifecycle = apps.get_model("models", "ResourceInstanceLifecycle")
    resource_instance_lifecycle = ResourceInstanceLifecycle.objects.get(
        id="e9a8a2b0-63b5-47a3-bbc4-9c09c0e759b1"
    )
    resource_instance_lifecycle.delete()


def create_perpetual_resource_instance_lifecycle_states(apps, schema_editor):
    ResourceInstanceLifecycleState = apps.get_model(
        "models", "ResourceInstanceLifecycleState"
    )

    ResourceInstanceLifecycleState.objects.create(
        id=uuid.UUID("4e2a6b8e-2489-4377-9c9f-29cfbd3e76c8"),
        name=_("Perpetual"),
        action_label="",
        resource_instance_lifecycle_id=uuid.UUID(
            "e9a8a2b0-63b5-47a3-bbc4-9c09c0e759b1"
        ),
        is_initial_state=True,
        can_delete_resource_instances=True,
        can_edit_resource_instances=True,
    )


def remove_perpetual_resource_instance_lifecycle_states(apps, schema_editor):
    ResourceInstanceLifecycleState = apps.get_model(
        "models", "ResourceInstanceLifecycleState"
    )

    perpetual_state = ResourceInstanceLifecycleState.objects.get(
        id="4e2a6b8e-2489-4377-9c9f-29cfbd3e76c8"
    )

    perpetual_state.delete()


def create_default_resource_instance_lifecycle(apps, schema_editor):
    ResourceInstanceLifecycle = apps.get_model("models", "ResourceInstanceLifecycle")
    ResourceInstanceLifecycle.objects.create(
        id=uuid.UUID("7e3cce56-fbfb-4a4b-8e83-59b9f9e7cb75"),
        name=_("Standard"),
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
        name=_("Draft"),
        action_label=_("Revert to Draft"),
        resource_instance_lifecycle_id=uuid.UUID(
            "7e3cce56-fbfb-4a4b-8e83-59b9f9e7cb75"
        ),
        is_initial_state=True,
        can_delete_resource_instances=True,
        can_edit_resource_instances=True,
    )
    active_state = ResourceInstanceLifecycleState.objects.create(
        id=uuid.UUID("f75bb034-36e3-4ab4-8167-f520cf0b4c58"),
        name=_("Active"),
        action_label=_("Make Active"),
        resource_instance_lifecycle_id=uuid.UUID(
            "7e3cce56-fbfb-4a4b-8e83-59b9f9e7cb75"
        ),
        is_initial_state=False,
        can_delete_resource_instances=False,
        can_edit_resource_instances=True,
    )
    retired_state = ResourceInstanceLifecycleState.objects.create(
        id=uuid.UUID("d95d9c0e-0e2c-4450-93a3-d788b91abcc8"),
        name=_("Retired"),
        action_label=_("Retire"),
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


def add_default_resource_instance_lifecycles_to_graphs(apps, schema_editor):
    GraphModel = apps.get_model("models", "GraphModel")
    ResourceInstanceLifecycle = apps.get_model("models", "ResourceInstanceLifecycle")

    default_resource_instance_lifecycle = ResourceInstanceLifecycle.objects.get(
        id="7e3cce56-fbfb-4a4b-8e83-59b9f9e7cb75"
    )

    for graph_model in GraphModel.objects.all():
        if (
            graph_model.isresource
            and not graph_model.source_identifier
            and not graph_model.resource_instance_lifecycle
        ):
            graph_model.resource_instance_lifecycle = (
                default_resource_instance_lifecycle
            )
            graph_model.save()


def remove_default_resource_instance_lifecycles_from_graphs(apps, schema_editor):
    GraphModel = apps.get_model("models", "GraphModel")

    for graph_model in GraphModel.objects.all():
        graph_model.resource_instance_lifecycle = None
        graph_model.save()


class Migration(migrations.Migration):

    dependencies = [
        ("models", "11042_create_resource_instance_lifecycle"),
    ]

    operations = [
        migrations.AddField(
            model_name="resourceinstancelifecyclestate",
            name="previous_resource_instance_lifecycle_states",
            field=models.ManyToManyField(
                related_name="next_lifecycle_states",
                through="models.ResourceInstanceLifecycleStateFromXRef",
                symmetrical=False,
                to="models.resourceinstancelifecyclestate",
            ),
        ),
        migrations.AddField(
            model_name="resourceinstancelifecyclestate",
            name="next_resource_instance_lifecycle_states",
            field=models.ManyToManyField(
                related_name="previous_lifecycle_states",
                through="models.ResourceInstanceLifecycleStateToXRef",
                symmetrical=False,
                to="models.resourceinstancelifecyclestate",
            ),
        ),
        migrations.AddConstraint(
            model_name="resourceinstancelifecyclestate",
            constraint=models.UniqueConstraint(
                condition=models.Q(("is_initial_state", True)),
                fields=("resource_instance_lifecycle",),
                name="unique_initial_state_per_lifecycle",
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
        migrations.RunPython(
            create_perpetual_resource_instance_lifecycle,
            remove_perpetual_resource_instance_lifecycle,
        ),
        migrations.RunPython(
            create_perpetual_resource_instance_lifecycle_states,
            remove_perpetual_resource_instance_lifecycle_states,
        ),
        migrations.AddField(
            model_name="graphmodel",
            name="resource_instance_lifecycle",
            field=models.ForeignKey(
                null=True,
                on_delete=models.deletion.PROTECT,
                related_name="graphs",
                to="models.resourceinstancelifecycle",
            ),
        ),
        migrations.RunPython(
            add_default_resource_instance_lifecycles_to_graphs,
            remove_default_resource_instance_lifecycles_from_graphs,
        ),
        migrations.AddConstraint(
            model_name="graphmodel",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(isresource=False, resource_instance_lifecycle__isnull=True)
                    | models.Q(
                        isresource=True,
                        source_identifier__isnull=False,
                        resource_instance_lifecycle__isnull=True,
                    )
                    | models.Q(
                        isresource=True,
                        source_identifier__isnull=True,
                        resource_instance_lifecycle__isnull=False,
                    )
                ),
                name="resource_instance_lifecycle_conditional_null",
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
