from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    def forward_migrate(apps, schema_editor, with_create_permissions=True):
        manifest_image_model = apps.get_model("models", "ManifestImage")
        file_model = apps.get_model("models", "File")

        for manifest_image in manifest_image_model.objects.all():
            file = file_model.objects.create(
                fileid=manifest_image.imageid,
                path=manifest_image.image,
            )

            file.save()

    def reverse_migrate(apps, schema_editor, with_create_permissions=True):
        manifest_image_model = apps.get_model("models", "ManifestImage")
        file_model = apps.get_model("models", "File")

        for file in file_model.objects.all():
            # not guaranteed accurate but should work for most cases,
            # ManifestImage does not have tile data
            if not file.tile_id:
                manifest_image = manifest_image_model.objects.create(
                    imageid=file.fileid,
                    image=file.path,
                )

                manifest_image.save()

    dependencies = [
        ("models", "7262_report_template_data_fetch_bool"),
    ]

    operations = [migrations.RunPython(forward_migrate, reverse_migrate)]
