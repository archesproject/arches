

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '5076_adds_map_card_configs'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            update card_components
                set defaultconfig = jsonb_set(defaultconfig, '{selectSourceLayer}', '""')
                where componentid = '3c103484-22d1-4ca9-a9f3-eb3902d567ac';
            update cards
                set config = jsonb_set(config, '{selectSourceLayer}', '""')
                where componentid = '3c103484-22d1-4ca9-a9f3-eb3902d567ac';
            """,
            reverse_sql="""
            update card_components
                set defaultconfig = defaultconfig - 'selectSourceLayer'
                where componentid = '3c103484-22d1-4ca9-a9f3-eb3902d567ac';
            update cards
                set config = config - 'selectSourceLayer'
                where componentid = '3c103484-22d1-4ca9-a9f3-eb3902d567ac';
            """,
        ),
    ]
