from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '5407_remove_tileserver'),
    ]

    operations = [
        migrations.RunSQL(
            """
            update nodes
            set config =  config - 'cacheTiles'
            where datatype = 'geojson-feature-collection';

            update nodes
            set config =  config - 'autoManageCache'
            where datatype = 'geojson-feature-collection';

            update d_data_types
            set defaultconfig = defaultconfig - 'cacheTiles'
            where datatype = 'geojson-feature-collection';

            update d_data_types
            set defaultconfig = defaultconfig - 'autoManageCache'
            where datatype = 'geojson-feature-collection';
            """,
            """
            update d_data_types
            set defaultconfig = jsonb_set(defaultconfig, '{cacheTiles}', 'false')
            where datatype = 'geojson-feature-collection';

            update nodes
            set config = jsonb_set(config, '{cacheTiles}', 'false')
            where datatype = 'geojson-feature-collection';

            update d_data_types
            set defaultconfig = jsonb_set(defaultconfig, '{autoManageCache}', 'false')
            where datatype = 'geojson-feature-collection';

            update nodes
            set config = jsonb_set(config, '{autoManageCache}', 'false')
            where datatype = 'geojson-feature-collection';
            """
        ),
    ]
