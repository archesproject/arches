# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0008_4_0_1'),
    ]

    operations = [
        migrations.RunSQL("""
                DELETE FROM functions WHERE functionid = '60000000-0000-0000-0000-000000000002'
            """,
            """
                INSERT INTO functions(functionid, modulename, classname, functiontype, name, description, defaultconfig, component)
                    VALUES ('60000000-0000-0000-0000-000000000002', 'required_nodes.py', 'RequiredNodesFunction', 'validation', 'Define Required Nodes', 'Define which values are required for a user to save card', '{"required_nodes":"{}"}', 'views/components/functions/required-nodes');
            """),
        ]
