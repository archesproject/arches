# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.db import migrations, models
from django.core import management

class Migration(migrations.Migration):

    dependencies = [
        ('models', '2402_node_to_node'),
    ]

    operations = [
            migrations.RunSQL("""
                UPDATE d_data_types
                SET defaultconfig = jsonb_build_object('trueLabel', '', 'falseLabel', '') || COALESCE(defaultconfig, '{}'::jsonb)
                WHERE datatype = 'boolean';
                --
                UPDATE nodes AS n
                SET config = COALESCE(n.config, '{}'::jsonb) || jsonb_build_object('trueLabel', c.config->>'trueLabel', 'falseLabel', c.config->>'falseLabel')
                FROM cards_x_nodes_x_widgets AS c
                WHERE n.nodeid = c.nodeid
                AND n.datatype = 'boolean';
                --
                UPDATE cards_x_nodes_x_widgets
                SET config = config - 'falseLabel'
                WHERE nodeid in (SELECT nodeid from nodes WHERE datatype = 'boolean');

                UPDATE cards_x_nodes_x_widgets
                SET config = config - 'trueLabel'
                WHERE nodeid in (SELECT nodeid from nodes WHERE datatype = 'boolean');

                """,

                """
                UPDATE d_data_types
                SET defaultconfig = defaultconfig - 'trueLabel'
                WHERE datatype = 'boolean';

                UPDATE d_data_types
                SET defaultconfig = defaultconfig - 'falseLabel'
                WHERE datatype = 'boolean';
                --
                UPDATE nodes
                SET config = config - 'trueLabel'
                WHERE datatype = 'boolean';

                UPDATE nodes
                SET config = config - 'falseLabel'
                WHERE datatype = 'boolean';
                --
                UPDATE cards_x_nodes_x_widgets AS n
                SET config = COALESCE(n.config, '{}'::jsonb) || jsonb_build_object('trueLabel', c.config->>'trueLabel', 'falseLabel', c.config->>'falseLabel')
                FROM nodes AS c
                WHERE n.nodeid = c.nodeid
                AND c.datatype = 'boolean';
                """),
    ]
