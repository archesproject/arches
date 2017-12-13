# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.db import migrations, models
from django.core import management

class Migration(migrations.Migration):

    dependencies = [
        ('models', '2709_map_widget_default_value'),
    ]

    operations = [
            migrations.RunSQL(
                """
                    update widgets
                    	set defaultconfig = (SELECT defaultconfig || jsonb_build_object('defaultValue',null) FROM widgets WHERE name = 'radio-boolean-widget')
                    	WHERE name = 'radio-boolean-widget';
                    update cards_x_nodes_x_widgets
                    	set config = (SELECT config || jsonb_build_object('defaultValue', null) FROM widgets WHERE name = 'radio-boolean-widget')
                    	WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'radio-boolean-widget') and config @> '{"defaultValue":""}';

                """,
                """
                    update widgets
                    	set defaultconfig = (SELECT defaultconfig || jsonb_build_object('defaultValue','') FROM widgets WHERE name = 'radio-boolean-widget')
                    	WHERE name = 'radio-boolean-widget';
                    update cards_x_nodes_x_widgets
                    	set config = (SELECT config || jsonb_build_object('defaultValue', '') FROM widgets WHERE name = 'radio-boolean-widget')
                    	WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'radio-boolean-widget') and config @> '{"defaultValue":null}';
                """
                ),
            migrations.RunSQL(
                """
                    update widgets
                    	set defaultconfig = (SELECT defaultconfig || jsonb_build_object('defaultValue',null) FROM widgets WHERE name = 'switch-widget')
                    	WHERE name = 'switch-widget';
                    update cards_x_nodes_x_widgets
                    	set config = (SELECT config || jsonb_build_object('defaultValue', null) FROM widgets WHERE name = 'switch-widget')
                    	WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'switch-widget') and config @> '{"defaultValue":""}';

                """,
                """
                    update widgets
                    	set defaultconfig = (SELECT defaultconfig || jsonb_build_object('defaultValue','') FROM widgets WHERE name = 'switch-widget')
                    	WHERE name = 'switch-widget';
                    update cards_x_nodes_x_widgets
                    	set config = (SELECT config || jsonb_build_object('defaultValue', '') FROM widgets WHERE name = 'switch-widget')
                    	WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'switch-widget') and config @> '{"defaultValue":null}';
                """
                ),
    ]
