# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.db import migrations, models
from django.core import management

class Migration(migrations.Migration):

    dependencies = [
        ('models', '2591_formatted_numbers'),
    ]

    operations = [
            migrations.RunSQL("""
                    update widgets
                    	set defaultconfig = (SELECT defaultconfig || jsonb_build_object('defaultValue', '') FROM widgets WHERE name = 'map-widget')
                    	WHERE name = 'map-widget';
                    update cards_x_nodes_x_widgets
                    	set config = (SELECT config || jsonb_build_object('defaultValue', '') FROM widgets WHERE name = 'map-widget')
                    	WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'map-widget');

                    update widgets
                          set defaultconfig = (SELECT defaultconfig || jsonb_build_object('defaultValueType', '') FROM widgets WHERE name = 'map-widget')
                          WHERE name = 'map-widget';
                        update cards_x_nodes_x_widgets
                          set config = (SELECT config || jsonb_build_object('defaultValueType', '') FROM widgets WHERE name = 'map-widget')
                          WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'map-widget');
                """,
                """
                    update widgets
                    	set defaultconfig = defaultconfig - 'defaultValue'
                    	WHERE name = 'map-widget';
                    update widgets
                    	set defaultconfig = defaultconfig - 'defaultValueType'
                    	WHERE name = 'map-widget';
                    update cards_x_nodes_x_widgets
                    	set config = config - 'defaultValue'
                    	WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'map-widget');
                    update cards_x_nodes_x_widgets
                    	set config = config - 'defaultValueType'
                    	WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'map-widget');
                """
                ),
    ]
