# -*- coding: utf-8 -*-


from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('models', '2533_duplicated_concept_relation_import'),
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
                VALUES ('edtf', 'fa fa-file-code-o', 'datatypes.py', 'EDTFDataType', '{"fuzzy_year_padding": 1, "fuzzy_month_padding": 1, "fuzzy_day_padding":1, 
                    "fuzzy_season_padding":12, "multiplier_if_uncertain":1, "multiplier_if_approximate":1, "multiplier_if_both":1}', 
                    'views/components/datatypes/edtf', 'edtf-datatype-config', FALSE, 'adfd15ce-dbab-11e7-86d1-0fcf08612b27', TRUE);
            """,
            """
            DELETE FROM d_data_types WHERE datatype = 'edtf';
            DELETE from widgets WHERE widgetid = 'adfd15ce-dbab-11e7-86d1-0fcf08612b27';
        """),
    ]
