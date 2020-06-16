# -*- coding: utf-8 -*-


import os
from django.db import migrations, models
from django.core import management

class Migration(migrations.Migration):

    dependencies = [
        ('models', '2963_tile_fk_on_file_model'),
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
