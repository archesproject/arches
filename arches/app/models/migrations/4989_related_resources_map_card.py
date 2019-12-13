from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "5076_adds_map_card_sourcelayer_config"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            INSERT INTO card_components(componentid, name, description, component, componentname, defaultconfig)
                VALUES ('2d2e0ca3-089c-4f4c-96a5-fb7eb53963bd', 'Related Resources Map Card', 'related resources map card UI', 'views/components/cards/related-resources-map', 'related-resources-map-card', '{"selectSource": "", "selectSourceLayer": ""}');
            """,
            reverse_sql="""
            UPDATE cards SET componentid = 'f05e4d3a-53c1-11e8-b0ea-784f435179ea' WHERE componentid = '2d2e0ca3-089c-4f4c-96a5-fb7eb53963bd';
            DELETE FROM card_components WHERE componentid = '2d2e0ca3-089c-4f4c-96a5-fb7eb53963bd';
            """,
        ),
    ]
