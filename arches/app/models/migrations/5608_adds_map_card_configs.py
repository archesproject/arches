from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "5712_update_sys_setting"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            update card_components
                set defaultconfig = jsonb_set(defaultconfig, '{zoom}', '0')
                where componentid = '3c103484-22d1-4ca9-a9f3-eb3902d567ac';
            update card_components
                set defaultconfig = jsonb_set(defaultconfig, '{centerX}', '0')
                where componentid = '3c103484-22d1-4ca9-a9f3-eb3902d567ac';
            update card_components
                set defaultconfig = jsonb_set(defaultconfig, '{centerY}', '0')
                where componentid = '3c103484-22d1-4ca9-a9f3-eb3902d567ac';
            update cards
                set config = jsonb_set(config, '{zoom}', '0')
                where componentid = '3c103484-22d1-4ca9-a9f3-eb3902d567ac';
            update cards
                set config = jsonb_set(config, '{centerX}', '0')
                where componentid = '3c103484-22d1-4ca9-a9f3-eb3902d567ac';
            update cards
                set config = jsonb_set(config, '{centerY}', '0')
                where componentid = '3c103484-22d1-4ca9-a9f3-eb3902d567ac';
            """,
            reverse_sql="""
            update card_components
                set defaultconfig = defaultconfig - 'zoom'
                where componentid = '3c103484-22d1-4ca9-a9f3-eb3902d567ac';
            update card_components
                set defaultconfig = defaultconfig - 'centerX'
                where componentid = '3c103484-22d1-4ca9-a9f3-eb3902d567ac';
            update card_components
                set defaultconfig = defaultconfig - 'centerY'
                where componentid = '3c103484-22d1-4ca9-a9f3-eb3902d567ac';
            update cards
                set config = config - 'zoom'
                where componentid = '3c103484-22d1-4ca9-a9f3-eb3902d567ac';
            update cards
                set config = config - 'centerX'
                where componentid = '3c103484-22d1-4ca9-a9f3-eb3902d567ac';
            update cards
                set config = config - 'centerY'
                where componentid = '3c103484-22d1-4ca9-a9f3-eb3902d567ac';
            """,
        ),
    ]
