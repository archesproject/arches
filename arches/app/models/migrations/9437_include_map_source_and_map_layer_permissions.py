from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('models', '9436_relational_view_null_geom_support'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='maplayer',
            options={'default_permissions': (), 'managed': True, 'permissions': (('no_access_to_maplayer', 'No access to map layer'),)},
        ),
    ]