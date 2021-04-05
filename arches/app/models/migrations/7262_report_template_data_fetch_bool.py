from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "7224_url_datatype"),
    ]

    operations = [
        migrations.AddField(
            model_name="reporttemplate",
            name="preload_resource_data",
            field=models.BooleanField(default=True),
        ),
    ]
