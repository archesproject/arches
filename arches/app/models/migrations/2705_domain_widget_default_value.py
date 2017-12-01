# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.db import migrations, models
from django.core import management

class Migration(migrations.Migration):

    dependencies = [
        ('models', '2701_boolean_widget_default_value'),
    ]

    operations = [
            migrations.RunSQL("""
                    update widgets
                    	set defaultconfig = (SELECT defaultconfig || jsonb_build_object('defaultValue', '') FROM widgets WHERE name = 'domain-select-widget')
                    	WHERE name = 'domain-select-widget';
                    update cards_x_nodes_x_widgets
                    	set config = (SELECT config || jsonb_build_object('defaultValue', '') FROM widgets WHERE name = 'domain-select-widget')
                    	WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'domain-select-widget');


                """,
                """
                    update widgets
                    	set defaultconfig = defaultconfig - 'defaultValue'
                    	WHERE name = 'domain-select-widget';
                    update cards_x_nodes_x_widgets
                    	set config = config - 'defaultValue'
                    	WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'domain-select-widget');
                """
                ),
            migrations.RunSQL("""
                    update widgets
                        set defaultconfig = (SELECT defaultconfig || jsonb_build_object('defaultValue', '') FROM widgets WHERE name = 'domain-radio-widget')
                        WHERE name = 'domain-radio-widget';
                    update cards_x_nodes_x_widgets
                        set config = (SELECT config || jsonb_build_object('defaultValue', '') FROM widgets WHERE name = 'domain-radio-widget')
                        WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'domain-radio-widget');


                """,
                """
                    update widgets
                        set defaultconfig = defaultconfig - 'defaultValue'
                        WHERE name = 'domain-radio-widget';
                    update cards_x_nodes_x_widgets
                        set config = config - 'defaultValue'
                        WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'domain-radio-widget');
                """
                ),
            migrations.RunSQL("""
                    update widgets
                        set defaultconfig = (SELECT defaultconfig || jsonb_build_object('defaultValue', '') FROM widgets WHERE name = 'domain-multiselect-widget')
                        WHERE name = 'domain-multiselect-widget';
                    update cards_x_nodes_x_widgets
                        set config = (SELECT config || jsonb_build_object('defaultValue', '') FROM widgets WHERE name = 'domain-multiselect-widget')
                        WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'domain-multiselect-widget');


                """,
                """
                    update widgets
                        set defaultconfig = defaultconfig - 'defaultValue'
                        WHERE name = 'domain-multiselect-widget';
                    update cards_x_nodes_x_widgets
                        set config = config - 'defaultValue'
                        WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'domain-multiselect-widget');
                """
                ),
            migrations.RunSQL("""
                    update widgets
                        set defaultconfig = (SELECT defaultconfig || jsonb_build_object('defaultValue', '') FROM widgets WHERE name = 'domain-checkbox-widget')
                        WHERE name = 'domain-checkbox-widget';
                    update cards_x_nodes_x_widgets
                        set config = (SELECT config || jsonb_build_object('defaultValue', '') FROM widgets WHERE name = 'domain-checkbox-widget')
                        WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'domain-checkbox-widget');


                """,
                """
                    update widgets
                        set defaultconfig = defaultconfig - 'defaultValue'
                        WHERE name = 'domain-checkbox-widget';
                    update cards_x_nodes_x_widgets
                        set config = config - 'defaultValue'
                        WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'domain-checkbox-widget');
                """
                ),
    ]
