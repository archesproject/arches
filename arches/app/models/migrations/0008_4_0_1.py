# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2017-09-25 12:27


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0007_4_0_1"),
    ]

    operations = [
        migrations.AddField(
            model_name="node",
            name="isrequired",
            field=models.BooleanField(default=False),
        ),
    ]
