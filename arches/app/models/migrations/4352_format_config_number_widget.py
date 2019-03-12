# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.db import migrations, models
from django.core import management

class Migration(migrations.Migration):

    dependencies = [
        ('models', '4384_adds_rerender_widget_config'),
    ]

    operations = [
            migrations.RunSQL("""
                    update widgets
                    	set defaultconfig = jsonb_set(defaultconfig, '{format}', '""')
                    	where datatype = 'number';
                    update cards_x_nodes_x_widgets
                    	set config = jsonb_set(config, '{format}', '""')
                    	WHERE nodeid IN (SELECT nodeid FROM nodes WHERE datatype = 'number');
                """,
                """
                    update widgets
                    	set defaultconfig = defaultconfig - 'format'
                    	where datatype = 'number';
                    update cards_x_nodes_x_widgets
                    	set config = config - 'format'
                    	WHERE nodeid IN (SELECT nodeid FROM nodes WHERE datatype = 'number');
                """),
    ]
