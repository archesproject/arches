from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '3713_unload_ontolgy'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            INSERT INTO card_components(componentid, name, description, component, componentname, defaultconfig)
                VALUES ('2d2e0ca3-089c-4f4c-96a5-fb7eb53963bd', 'Related Resources Map Card', 'related resources map card UI', 'views/components/cards/related-resources-map', 'related-resources-map-card', '{"selectSource": "", "selectSourceLayer": ""}');
            """,
            reverse_sql="""
            DELETE FROM card_components WHERE componentid = '2d2e0ca3-089c-4f4c-96a5-fb7eb53963bd';
            """,
        ),
    ]
