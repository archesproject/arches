# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.db import migrations, models
from django.core import management

class Migration(migrations.Migration):

    dependencies = [
        ('models', '2532_boolean_datatype_display_value'),
    ]

    operations = [
            migrations.RunSQL("""
                update nodes n
                	set config = jsonb_set(config, '{graphid}', (
                		select jsonb_agg(config->'graphid')
                		from nodes n1
                		where n1.nodeid = n.nodeid
                	))
                	where datatype in ('resource-instance', 'resource-instance-list')
                	and config->'graphid' is not null;
                """,
                """
                update nodes n
                	set config = jsonb_set(config, '{graphid}', config->'graphid'->0)
                	where datatype in ('resource-instance', 'resource-instance-list')
                	and config->'graphid' is not null;
                """),
    ]
