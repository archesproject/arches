from django.db import migrations


FUNCTION_ID = "00b2d15a-fda0-4578-b79a-784e4138664b"


def add_multicard_resource_descriptor(apps, schema_editor):
    Function = apps.get_model("models", "Function")
    Function.objects.get_or_create(
        functionid=FUNCTION_ID,
        defaults={
            "name": "Multi-Card Resource Descriptor",
            "functiontype": "primarydescriptors",
            "description": "Configure the name, description, and map popup of a resource",
            "defaultconfig": {
                "descriptor_types": {
                    "name": {"nodegroup_id": "", "string_template": ""},
                    "map_popup": {"nodegroup_id": "", "string_template": ""},
                    "description": {"nodegroup_id": "", "string_template": ""},
                }
            },
            "modulename": "multicard_resource_descriptor.py",
            "classname": "MulticardResourceDescriptor",
            "component": "views/components/functions/multicard-resource-descriptor",
        },
    )


def remove_multicard_resource_descriptor(apps, schema_editor):
    Function = apps.get_model("models", "Function")
    Function.objects.filter(functionid=FUNCTION_ID).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("models", "12778_add_loadstaging_index"),
    ]

    operations = [
        migrations.RunPython(
            add_multicard_resource_descriptor,
            remove_multicard_resource_descriptor,
        )
    ]
