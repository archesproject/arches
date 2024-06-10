import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "9944_improve_refresh_relationship_function"),
    ]

    def gen_uuid(apps, schema_editor):
        IIIFManifest = apps.get_model("models", "IIIFManifest")
        for row in IIIFManifest.objects.all():
            row.globalid = uuid.uuid4()
            row.save(update_fields=["globalid"])

    operations = [
        migrations.AddField(
            model_name="iiifmanifest",
            name="globalid",
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name="iiifmanifest",
            name="globalid",
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
