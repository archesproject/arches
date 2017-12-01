# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.db import migrations, models
from django.core import management

class Migration(migrations.Migration):

    dependencies = [
        ('models', '2705_domain_widget_default_value'),
    ]

    operations = [
            migrations.RunSQL("""
                    update widgets
                    	set defaultconfig = (SELECT defaultconfig || jsonb_build_object('defaultValue', '') FROM widgets WHERE name = 'concept-select-widget')
                    	WHERE name = 'concept-select-widget';
                    update cards_x_nodes_x_widgets
                    	set config = (SELECT config || jsonb_build_object('defaultValue', '') FROM widgets WHERE name = 'concept-select-widget')
                    	WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'concept-select-widget');


                """,
                """
                    update widgets
                    	set defaultconfig = defaultconfig - 'defaultValue'
                    	WHERE name = 'concept-select-widget';
                    update cards_x_nodes_x_widgets
                    	set config = config - 'defaultValue'
                    	WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'concept-select-widget');
                """
                ),
            migrations.RunSQL("""
                    update widgets
                        set defaultconfig = (SELECT defaultconfig || jsonb_build_object('defaultValue', '') FROM widgets WHERE name = 'concept-radio-widget')
                        WHERE name = 'concept-radio-widget';
                    update cards_x_nodes_x_widgets
                        set config = (SELECT config || jsonb_build_object('defaultValue', '') FROM widgets WHERE name = 'concept-radio-widget')
                        WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'concept-radio-widget');


                """,
                """
                    update widgets
                        set defaultconfig = defaultconfig - 'defaultValue'
                        WHERE name = 'concept-radio-widget';
                    update cards_x_nodes_x_widgets
                        set config = config - 'defaultValue'
                        WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'concept-radio-widget');
                """
                ),
            migrations.RunSQL("""
                    update widgets
                        set defaultconfig = (SELECT defaultconfig || jsonb_build_object('defaultValue', '') FROM widgets WHERE name = 'concept-multiselect-widget')
                        WHERE name = 'concept-multiselect-widget';
                    update cards_x_nodes_x_widgets
                        set config = (SELECT config || jsonb_build_object('defaultValue', '') FROM widgets WHERE name = 'concept-multiselect-widget')
                        WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'concept-multiselect-widget');


                """,
                """
                    update widgets
                        set defaultconfig = defaultconfig - 'defaultValue'
                        WHERE name = 'concept-multiselect-widget';
                    update cards_x_nodes_x_widgets
                        set config = config - 'defaultValue'
                        WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'concept-multiselect-widget');
                """
                ),
            migrations.RunSQL("""
                    update widgets
                        set defaultconfig = (SELECT defaultconfig || jsonb_build_object('defaultValue', '') FROM widgets WHERE name = 'concept-checkbox-widget')
                        WHERE name = 'concept-checkbox-widget';
                    update cards_x_nodes_x_widgets
                        set config = (SELECT config || jsonb_build_object('defaultValue', '') FROM widgets WHERE name = 'concept-checkbox-widget')
                        WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'concept-checkbox-widget');


                """,
                """
                    update widgets
                        set defaultconfig = defaultconfig - 'defaultValue'
                        WHERE name = 'concept-checkbox-widget';
                    update cards_x_nodes_x_widgets
                        set config = config - 'defaultValue'
                        WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'concept-checkbox-widget');
                """
                ),
    ]
