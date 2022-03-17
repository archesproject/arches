from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("models", "8085_relational_data_model_handle_dates"), ]
    operations = [
        migrations.RunSQL(
            """
            update functions
                set defaultconfig = jsonb_concat(json_build_object('descriptor_types',
                                                 json_build_object('name', defaultconfig -> 'name',
                                                                   'description', defaultconfig -> 'description',
                                                                   'map_popup', defaultconfig -> 'map_popup'))::jsonb,
                                                 ('{"module": "arches.app.functions.primary_descriptors", '||
                                                 '"class_name": "PrimaryDescriptorsFunction" }')::jsonb)
                where functionid = '60000000-0000-0000-0000-000000000001';


               update functions_x_graphs
                    set config = jsonb_concat(json_build_object('descriptor_types',
                                             json_build_object('name', config -> 'name',
                                                               'description', config -> 'description',
                                                               'map_popup', config -> 'map_popup'))::jsonb,
                                             ('{"module": "arches.app.functions.primary_descriptors", '||
                                             '"class_name": "PrimaryDescriptorsFunction" }')::jsonb)
                    where functionid = '60000000-0000-0000-0000-000000000001';
            """
        )
    ]
