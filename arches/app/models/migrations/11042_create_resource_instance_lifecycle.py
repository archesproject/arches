import uuid
from django.db import migrations, models
from django.utils.translation import gettext as _

import arches.app.models.fields.i18n
import arches.app.utils.betterJSONSerializer


class Migration(migrations.Migration):

    dependencies = [
        ("models", "9525_add_published_graph_edits"),
    ]

    operations = [
        migrations.CreateModel(
            name="ResourceInstanceLifecycle",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        primary_key=True,
                        serialize=False,
                        default=uuid.uuid4,
                    ),
                ),
                ("name", arches.app.models.fields.i18n.I18n_TextField()),
            ],
            options={
                "db_table": "resource_instance_lifecycles",
                "managed": True,
            },
        ),
        migrations.CreateModel(
            name="ResourceInstanceLifecycleState",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        primary_key=True,
                        serialize=False,
                        default=uuid.uuid4,
                    ),
                ),
                (
                    "name",
                    arches.app.models.fields.i18n.I18n_TextField(
                        default="",
                        encoder=arches.app.utils.betterJSONSerializer.JSONSerializer,
                    ),
                ),
                (
                    "action_label",
                    arches.app.models.fields.i18n.I18n_TextField(
                        default="",
                        encoder=arches.app.utils.betterJSONSerializer.JSONSerializer,
                    ),
                ),
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
                "permissions": (
                    (
                        "can_edit_all_resource_instance_lifecycle_states",
                        "Can edit all resource instance lifecycle states",
                    ),
                    (
                        "can_delete_all_resource_instance_lifecycle_states",
                        "Can delete all resource instance lifecycle states",
                    ),
                ),
                "managed": True,
            },
        ),
        migrations.CreateModel(
            name="ResourceInstanceLifecycleStateFromXRef",
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
                        related_name="from_xref_next_lifecycle_states",
                        to="models.resourceinstancelifecyclestate",
                    ),
                ),
                (
                    "resource_instance_lifecycle_state_to",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="from_xref_previous_lifecycle_states",
                        to="models.resourceinstancelifecyclestate",
                    ),
                ),
            ],
            options={
                "db_table": "resource_instance_lifecycle_states_from_xref",
                "managed": True,
            },
        ),
        migrations.CreateModel(
            name="ResourceInstanceLifecycleStateToXRef",
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
                        related_name="to_xref_next_lifecycle_states",
                        to="models.resourceinstancelifecyclestate",
                    ),
                ),
                (
                    "resource_instance_lifecycle_state_to",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="to_xref_previous_lifecycle_states",
                        to="models.resourceinstancelifecyclestate",
                    ),
                ),
            ],
            options={
                "db_table": "resource_instance_lifecycle_states_to_xref",
                "managed": True,
            },
        ),
    ]
