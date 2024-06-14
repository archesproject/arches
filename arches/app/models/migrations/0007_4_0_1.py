# -*- coding: utf-8 -*-


import os
from django.db import migrations, models
from django.core import management


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0006_4_0_1"),
    ]

    operations = [
        migrations.RunSQL(
            """
                    update d_data_types
                    	set defaultconfig = jsonb_set(defaultconfig, '{simplification}', '0.3')
                    	where datatype = 'geojson-feature-collection';
                    update nodes
                    	set config = jsonb_set(config, '{simplification}', '0.3')
                    	where datatype = 'geojson-feature-collection';
                """,
            """
                    update d_data_types
                    	set defaultconfig = defaultconfig - 'simplification'
                    	where datatype = 'geojson-feature-collection';
                    update nodes
                    	set config = config - 'simplification'
                    	where datatype = 'geojson-feature-collection';
                """,
        ),
    ]
