# Generated by Django 3.2.18 on 2023-06-05 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '9558_add_plugin_help'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='overlaysortorder',
            field=models.IntegerField(default=0),
        ),
    ]





