from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "5477_fix_makemigrations"),
    ]

    operations = [
        migrations.AddField(
            model_name="node",
            name="fieldname",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="nodegroup",
            name="exportable",
            field=models.BooleanField(default=False, null=True),
        ),
    ]
