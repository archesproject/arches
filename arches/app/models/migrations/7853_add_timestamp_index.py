from django.db import migrations, models
import arches.app.models.models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "12000_update_serialized_graph_functions"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="editlog",
            index=models.Index(
                condition=models.Q(
                    models.Q(
                        (
                            "resourceclassid",
                            arches.app.models.utils.get_system_settings_resource_model_id,
                        ),
                        _negated=True,
                    ),
                    models.Q(("note", "resource creation"), _negated=True),
                ),
                fields=["timestamp"],
                name="edit_log_timestamp_idx",
            ),
        ),
    ]
