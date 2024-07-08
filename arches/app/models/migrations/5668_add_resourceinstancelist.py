# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("models", "3693_ontology_in_pkgs"),
    ]

    operations = [
        migrations.RunSQL(
            """
            UPDATE public.d_data_types
            SET classname='ResourceInstanceListDataType'
            WHERE datatype='resource-instance-list';
            """,
            """
            UPDATE public.d_data_types
            SET classname='ResourceInstanceDataType'
            WHERE datatype='resource-instance-list';
            """,
        )
    ]
