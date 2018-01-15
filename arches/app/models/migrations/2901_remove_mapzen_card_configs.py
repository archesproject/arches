# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.db import migrations, models
from django.core import management

class Migration(migrations.Migration):

    dependencies = [
        ('models', '2595_file_upload_function'),
    ]

    operations = [
        migrations.RunSQL(
        """
            update cards_x_nodes_x_widgets SET config = jsonb_set(config, '{geocodeProvider}', '"10000000-0000-0000-0000-010000000000"') where config @> '{"geocodeProvider": "10000000-0000-0000-0000-010000000001"}' or config  @> '{"geocodeProvider": "MapzenGeocoder"}';
        """,
        """
            update cards_x_nodes_x_widgets SET config = jsonb_set(config, '{geocodeProvider}', '"10000000-0000-0000-0000-010000000001"') where config @> '{"geocodeProvider": "10000000-0000-0000-0000-010000000000"}';
        """),
    ]
