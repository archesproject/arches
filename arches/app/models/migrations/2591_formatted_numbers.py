# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.db import migrations, models
from django.core import management

class Migration(migrations.Migration):

  dependencies = [
      ('models', '2626_mobilesurveymodel_datadownload'),
  ]

  operations = [
          migrations.RunSQL("""
              update widgets set defaultconfig = '{"max":"","defaultValue":"","placeholder":"Enter number","width":"100%","min":"", "step":"", "precision":"", "prefix":"", "suffix":""}'  where name = 'number-widget';

              update cards_x_nodes_x_widgets
                    set config = (SELECT config || jsonb_build_object('step', '') FROM widgets WHERE name = 'number-widget')
                    WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'number-widget');
              update cards_x_nodes_x_widgets
                    set config = (SELECT config || jsonb_build_object('precision', '') FROM widgets WHERE name = 'number-widget')
                    WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'number-widget');
              update cards_x_nodes_x_widgets
                    set config = (SELECT config || jsonb_build_object('prefix', '') FROM widgets WHERE name = 'number-widget')
                    WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'number-widget');
              update cards_x_nodes_x_widgets
                    set config = (SELECT config || jsonb_build_object('suffix', '') FROM widgets WHERE name = 'number-widget')
                    WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'number-widget');
              """,
              """
                  update widgets set defaultconfig = defaultconfig - 'step' WHERE name = 'number-widget';
                  update widgets set defaultconfig = defaultconfig - 'precision' WHERE name = 'number-widget';
                  update widgets set defaultconfig = defaultconfig - 'prefix' WHERE name = 'number-widget';
                  update widgets set defaultconfig = defaultconfig - 'suffix' WHERE name = 'number-widget';
                  update cards_x_nodes_x_widgets set config = config - 'step' WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'number-widget');
                  update cards_x_nodes_x_widgets set config = config - 'precision' WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'number-widget');
                  update cards_x_nodes_x_widgets set config = config - 'prefix' WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'number-widget');
                  update cards_x_nodes_x_widgets set config = config - 'suffix' WHERE widgetid in (SELECT widgetid FROM widgets WHERE name = 'number-widget');
              """),
  ]
