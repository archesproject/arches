from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("models", "9604_fix_inefficient_trigger"),
    ]

    operations = [
        migrations.AddField(
            model_name="maplayer",
            name="ispublic",
            field=models.BooleanField(blank=False, null=False, default=True),
        ),
    ]
