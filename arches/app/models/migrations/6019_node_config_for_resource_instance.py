from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "6014_bidirectional_resource_instance"),
    ]

    def forward_migrate(apps, schema_editor, with_create_permissions=True):
        nodes = apps.get_model("models", "Node")
        datatypes = apps.get_model("models", "DDataType")
        for datatype in datatypes.objects.filter(
            datatype__in=["resource-instance", "resource-instance-list"]
        ):
            datatype.defaultconfig = {"graphs": []}
            datatype.save()

        for node in nodes.objects.filter(
            datatype__in=["resource-instance", "resource-instance-list"]
        ):
            old_config = node.config
            new_config = {"graphs": []}
            if old_config["graphid"]:
                for graphid in old_config["graphid"]:
                    new_config["graphs"].append(
                        {
                            "graphid": graphid,
                            "ontologyProperty": "",
                            "inverseOntologyProperty": "",
                        }
                    )

            node.config = new_config
            node.save()

    def reverse_migrate(apps, schema_editor, with_create_permissions=True):
        nodes = apps.get_model("models", "Node")
        datatypes = apps.get_model("models", "DDataType")
        for datatype in datatypes.objects.filter(
            datatype__in=["resource-instance", "resource-instance-list"]
        ):
            datatype.defaultconfig = {"graphid": None}
            datatype.save()

        for node in nodes.objects.filter(
            datatype__in=["resource-instance", "resource-instance-list"]
        ):
            new_config = node.config
            old_config = {"graphid": []}
            for config in new_config["graphs"]:
                old_config["graphid"].append(config["graphid"])
            node.config = old_config
            node.save()

    operations = [
        migrations.RunPython(forward_migrate, reverse_migrate),
    ]
