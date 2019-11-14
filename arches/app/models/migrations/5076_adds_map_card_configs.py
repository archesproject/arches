from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "4990_relax_tileserver_layer_constraints"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            update card_components
                set defaultconfig = '{"selectSource": "", "selectText": ""}'
                where componentid = '3c103484-22d1-4ca9-a9f3-eb3902d567ac';
            update cards
                set config = '{"selectSource": "", "selectText": ""}'
                where componentid = '3c103484-22d1-4ca9-a9f3-eb3902d567ac';
            """,
            reverse_sql="""
            update card_components
                set defaultconfig = null
                where componentid = '3c103484-22d1-4ca9-a9f3-eb3902d567ac';
            update cards
                set config = null
                where componentid = '3c103484-22d1-4ca9-a9f3-eb3902d567ac';
            """,
        ),
    ]
