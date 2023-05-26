from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('models', '9055_add_branch_publication_to_node'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='maplayer',
            options={'default_permissions': (), 
                     'managed': True, 
                     'permissions': (("no_access_to_maplayer", "No access to map layer"),
                                     ("read_maplayer", "Read map layer"),
                                     ("edit_maplayer", "Edit map layer"),
                                     ("delete_maplayer", "Delete map layer"))},
        ),
    ]