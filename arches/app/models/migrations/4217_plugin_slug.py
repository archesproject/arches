# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-10-22 16:47


import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ("models", "4202_plugin_model"),
    ]

    operations = [
        migrations.AddField(
            model_name="plugin",
            name="slug",
            field=models.TextField(
                null=True,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        re.compile("^[-a-zA-Z0-9_]+\\Z"),
                        "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.",
                        "invalid",
                    )
                ],
            ),
        ),
    ]
