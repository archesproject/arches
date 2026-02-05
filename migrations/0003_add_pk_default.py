import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("arches_component_lab", "0002_populate_widget_mappings"),
    ]

    operations = [
        migrations.AlterField(
            model_name="widgetmapping",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
            ),
        ),
    ]
