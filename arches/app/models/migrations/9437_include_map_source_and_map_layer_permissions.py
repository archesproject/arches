from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("models", "9219_update_load_event_task"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="maplayer",
            options={
                "default_permissions": (),
                "managed": True,
                "permissions": (
                    ("no_access_to_maplayer", "No Access"),
                    ("read_maplayer", "Read"),
                    ("write_maplayer", "Create/Update"),
                    ("delete_maplayer", "Delete"),
                ),
            },
        ),
    ]
