# Generated by Django 2.2.8 on 2019-12-20 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "5608_adds_map_card_configs"),
    ]

    operations = [
        migrations.AddField(
            model_name="searchexporthistory",
            name="downloadfile",
            field=models.FileField(
                blank=True, null=True, upload_to="export_deliverables"
            ),
        ),
    ]
