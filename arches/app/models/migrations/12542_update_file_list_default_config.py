from django.db import migrations
from arches.app.models.models import DDataType, Node


class Migration(migrations.Migration):

    def forward(apps, schema_editor):
        DDataType.objects.filter(
            defaultwidget="10000000-0000-0000-0000-000000000019"
        ).update(
            defaultconfig='{"maxFiles":null,"maxFileSize":null,"imagesOnly":false}'
        )

        file_list_nodes = Node.objects.filter(datatype="file-list")
        nodes_to_update = []
        for node in file_list_nodes:
            if node.config:
                config = node.config
                if "activateMax" in config:
                    config.pop("activateMax")
                    node.config = config
                    nodes_to_update.append(node)
        Node.objects.bulk_update(nodes_to_update, ["config"])

    def reverse(apps, schema_editor):
        DDataType.objects.filter(
            defaultwidget="10000000-0000-0000-0000-000000000019"
        ).update(
            defaultconfig='{"maxFiles":1,"activateMax":false,"maxFileSize":null,"imagesOnly":false}'
        )

        file_list_nodes = Node.objects.filter(datatype="file-list")
        nodes_to_update = []
        for node in file_list_nodes:
            if node.config:
                config = node.config
                if "activateMax" not in config:
                    config["activateMax"] = False
                    node.config = config
                    nodes_to_update.append(node)
        Node.objects.bulk_update(nodes_to_update, ["config"])

    dependencies = [
        ("models", "12394_resource_identifier"),
    ]

    operations = [migrations.RunPython(forward, reverse)]
