# -*- coding: utf-8 -*-


import os
from django.db import migrations, models
from django.core import management


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0005_4_0_1"),
    ]

    operations = [
        migrations.RunSQL(
            """
                UPDATE nodes AS n SET config = cast('{"fillColor": "rgba(' || trunc(random() * 255) || ',' || trunc(random() * 255) || ',' || trunc(random() * 255) || ',0.8)"}' as json)  FROM graphs AS g WHERE g.graphid = n.graphid AND g.isresource = true AND n.istopnode = true;
                """,
            """
                UPDATE nodes AS n SET config = null FROM graphs AS g WHERE g.graphid = n.graphid AND g.isresource = true AND n.istopnode = true;
                """,
        ),
    ]
