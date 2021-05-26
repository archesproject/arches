# Generated by Django 2.2.13 on 2021-05-25 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "7442_delete_manifest_images_table"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="node",
            name="unique_nodename_nodegroup",
        ),
        migrations.AddConstraint(
            model_name="node",
            constraint=models.UniqueConstraint(fields=("name", "nodegroupid"), name="unique_nodename_nodegroup"),
        ),
    ]
