# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.db import migrations, models
from django.core import management

class Migration(migrations.Migration):

    dependencies = [
        ('models', '2901_remove_mapzen'),
    ]

    operations = [
        migrations.RunSQL(
        """
        DELETE FROM functions_x_graphs WHERE functionid = '60000000-0000-0000-0000-000000000000';
        DELETE FROM functions WHERE functionid = '60000000-0000-0000-0000-000000000000';
        """,
        """
        INSERT INTO functions(functionid, modulename, classname, functiontype, name, description, defaultconfig, component)
            VALUES ('60000000-0000-0000-0000-000000000000', 'local_file_storage.py', 'LocalFileStorageFunction', 'node', 'Local File Upload', 'Sets the default storage mechanism for uploaded files', '{}', 'views/components/functions/local-file-storage');
        """),
    ]
