# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.db import migrations, models
from django.core import management

class Migration(migrations.Migration):

    dependencies = [
        ('models', '2704_string_widget_default_value'),
    ]

    operations = [
            migrations.RunSQL("""
                    update widgets
                    	set defaultconfig = (SELECT defaultconfig || jsonb_build_object('defaultValue', '') FROM widgets WHERE name = 'number-widget')
                    	WHERE name = 'number-widget';
                    update cards_x_nodes_x_widgets
                    	set config = (SELECT config || jsonb_build_object('defaultValue', '') FROM widgets WHERE name = 'number-widget')
                    	WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'number-widget');


                """,
                """
                    update widgets
                    	set defaultconfig = defaultconfig - 'defaultValue'
                    	WHERE name = 'number-widget';
                    update cards_x_nodes_x_widgets
                    	set config = config - 'defaultValue'
                    	WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'number-widget');
                """),
    ]
