from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("models", "9558_add_plugin_help"),
    ]

    def add_permissions(apps, schema_editor, with_create_permissions=True):
        db_alias = schema_editor.connection.alias
        Group = apps.get_model("auth", "Group")
        User = apps.get_model("auth", "User")
        resource_exporter_group = Group.objects.using(db_alias).create(
            name="Resource Exporter"
        )

        try:
            users = User.objects.using(db_alias)
            resource_exporter_group.user_set.add(*users)
            print("added users group")
        except Exception as e:
            print(e)

    def remove_permissions(apps, schema_editor, with_create_permissions=True):
        Group = apps.get_model("auth", "Group")

        try:
            Group.objects.filter(name__in=["Resource Exporter"]).delete()
            print("removed Resource Exporter group")
        except:
            pass

    operations = [
        migrations.RunPython(add_permissions, reverse_code=remove_permissions),
    ]
