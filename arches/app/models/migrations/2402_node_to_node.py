# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.db import migrations, models
from django.core import management

class Migration(migrations.Migration):

    dependencies = [
        ('models', '0014_4_0_2'),
    ]

    operations = [
            migrations.RunSQL("""
                INSERT INTO d_data_types(
                    datatype, iconclass, modulename,
                    classname, defaultconfig, configcomponent,
                    configname, isgeometric, defaultwidget,
                    issearchable
                ) VALUES (
                    'node-value',
                    'fa fa-external-link-square',
                    'datatypes.py',
                    'NodeValueDataType',
                    '{
                        "nodeid": null,
                        "property": null
                    }',
                    'views/components/datatypes/node-value',
                    'node-value-datatype-config',
                    FALSE,
                    'f5d6b190-bbf0-4dc9-b991-1debab8cb4a9',
                    TRUE
                );

                INSERT INTO widgets(
                    widgetid,
                    name,
                    component,
                    datatype,
                    defaultconfig
                ) VALUES (
                    'f5d6b190-bbf0-4dc9-b991-1debab8cb4a9',
                    'node-value-select',
                    'views/components/widgets/node-value-select',
                    'node-value',
                    '{
                        "placeholder": ""
                    }'
                );
                """,
                """
                DELETE FROM d_data_types
                    WHERE datatype = 'node-value';

                DELETE from widgets
                    WHERE widgetid = 'f5d6b190-bbf0-4dc9-b991-1debab8cb4a9';
                """),
    ]
