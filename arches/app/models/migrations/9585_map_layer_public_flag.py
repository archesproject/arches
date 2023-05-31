from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("models", "9437_include_map_source_and_map_layer_permissions"),
    ]

    operations = [
        migrations.AddField(
            model_name="maplayer",
            name="ispublic",
            field=models.IntegerField(blank=False, null=False, default=True),
        ),
    ]
