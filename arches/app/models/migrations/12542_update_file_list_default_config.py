from django.db import migrations
from arches.app.models.models import DDataType


class Migration(migrations.Migration):

    def forward(apps, schema_editor):
        DDataType.objects.filter(
            defaultwidget="10000000-0000-0000-0000-000000000019"
        ).update(
            defaultconfig='{"maxFiles":null,"maxFileSize":null,"imagesOnly":false}'
        )

    def reverse(apps, schema_editor):
        DDataType.objects.filter(
            defaultwidget="10000000-0000-0000-0000-000000000019"
        ).update(
            defaultconfig='{"maxFiles":1,"activateMax":false,"maxFileSize":null,"imagesOnly":false}'
        )

    dependencies = [
        ("models", "12394_resource_identifier"),
    ]

    operations = [migrations.RunPython(forward, reverse)]
