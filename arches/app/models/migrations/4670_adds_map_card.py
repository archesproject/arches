

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '4670_maplayer_legend'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            INSERT INTO card_components(componentid, name, description, component, componentname, defaultconfig)
                VALUES ('3c103484-22d1-4ca9-a9f3-eb3902d567ac', 'Map Card', 'Map card UI', 'views/components/cards/map', 'map-card', '{}');
            """,
            reverse_sql="""
            UPDATE cards SET componentid = 'f05e4d3a-53c1-11e8-b0ea-784f435179ea' WHERE componentid = '3c103484-22d1-4ca9-a9f3-eb3902d567ac';
            DELETE FROM card_components WHERE componentid = '3c103484-22d1-4ca9-a9f3-eb3902d567ac';
            """,
        ),
    ]
