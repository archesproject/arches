from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("models", "7442_move_data_from_manifest_images_table_to_files_table"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ManifestImage",
        ),
    ]
