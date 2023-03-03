from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("models", "9068_resource_model_view_defaults"),
    ]

    operations = [
        migrations.AddField(
            model_name="maplayer",
            name="sortorder",
            field=models.IntegerField(blank=False, null=False, default=0),
        ),
    ]
