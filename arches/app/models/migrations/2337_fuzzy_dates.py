# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('models', '2532_boolean_datatype_display_value'),
    ]

    operations = [
        migrations.RunSQL("""
            INSERT INTO widgets(widgetid, name, component, datatype, defaultconfig)
                VALUES ('adfd15ce-dbab-11e7-86d1-0fcf08612b27', 'edtf-widget', 'views/components/widgets/edtf', 'edtf', '{
                        "placeholder": "",
                        "defaultValue": ""
                    }'
                );
            INSERT INTO d_data_types(datatype, iconclass, modulename, classname, defaultconfig, 
                    configcomponent, configname, isgeometric, defaultwidget, issearchable) 
                VALUES ('edtf', 'fa fa-file-code-o', 'datatypes.py', 'EDTFDataType', '{"rdmCollection": null}', 
                    'views/components/datatypes/edtf', 'edtf-datatype-config', FALSE, 'adfd15ce-dbab-11e7-86d1-0fcf08612b27', TRUE);
            """,
            """
            DELETE FROM d_data_types WHERE datatype = 'edtf';
            DELETE from widgets WHERE widgetid = 'adfd15ce-dbab-11e7-86d1-0fcf08612b27';
        """),
    ]
