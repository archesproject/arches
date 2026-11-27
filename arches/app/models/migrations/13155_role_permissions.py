from django.db import migrations

# Each role permission is granted to the default group that used to be checked
# by name, so upgraded instances keep the same access.
ROLE_PERMISSIONS = {
    ("resourceinstance", "edit_resources"): (
        "Can use the resource editor",
        "Resource Editor",
    ),
    ("resourceinstance", "export_resources"): (
        "Can export search results",
        "Resource Exporter",
    ),
    ("spatialview", "manage_application"): (
        "Can administer map layers, spatial views and user preferences",
        "Application Administrator",
    ),
}


def grant_role_permissions(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Permission = apps.get_model("auth", "Permission")
    Group = apps.get_model("auth", "Group")

    for (model, codename), (name, group_name) in ROLE_PERMISSIONS.items():
        # post_migrate creates permissions only after every migration has run.
        content_type, _ = ContentType.objects.get_or_create(
            app_label="models", model=model
        )
        permission, _ = Permission.objects.get_or_create(
            codename=codename,
            content_type=content_type,
            defaults={"name": name},
        )
        permission.group_set.add(*Group.objects.filter(name=group_name))


def remove_role_permissions(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    for model, codename in ROLE_PERMISSIONS:
        Permission.objects.filter(
            codename=codename,
            content_type__app_label="models",
            content_type__model=model,
        ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("models", "13064_reference_datatype_relational_views"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="resourceinstance",
            options={
                "managed": True,
                "permissions": (
                    ("no_access_to_resourceinstance", "No Access"),
                    ("edit_resources", "Can use the resource editor"),
                    ("export_resources", "Can export search results"),
                ),
            },
        ),
        migrations.AlterModelOptions(
            name="spatialview",
            options={
                "managed": True,
                "permissions": (
                    (
                        "manage_application",
                        "Can administer map layers, spatial views and user preferences",
                    ),
                ),
            },
        ),
        migrations.RunPython(grant_role_permissions, remove_role_permissions),
    ]
