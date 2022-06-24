from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "7874_node_alias"),
    ]
    operations = [
        migrations.RunSQL(
            sql="""
            update functions
                set defaultconfig = ('{"descriptor_types": {"name": {"nodegroup_id": "", "string_template": ""}, '||
                                    '"map_popup": {"nodegroup_id": "", "string_template": ""}, '||
                                    '"description": {"nodegroup_id": "", "string_template": ""}}}')::jsonb
                where functionid = '60000000-0000-0000-0000-000000000001';

            update functions_x_graphs
                set config = jsonb_concat(jsonb_build_object('descriptor_types',
                                 jsonb_build_object('name', config -> 'name',
                                                    'description', config -> 'description',
                                                    'map_popup', config -> 'map_popup')),
                                                    jsonb_build_object('triggering_nodegroups', config->'triggering_nodegroups'))
                where functionid = '60000000-0000-0000-0000-000000000001';
            """,
            reverse_sql="""
               update functions_x_graphs
                   set config = jsonb_concat(config->'descriptor_types',
                            jsonb_build_object('triggering_nodegroups', config->'triggering_nodegroups'))
                   where functionid = '60000000-0000-0000-0000-000000000001';

                update functions
                    set defaultconfig = ('{"name": {"nodegroup_id": "", "string_template": ""}, '||
                                         '"map_popup": {"nodegroup_id": "", "string_template": ""}, '||
                                         '"description": {"nodegroup_id": "", "string_template": ""}}')::jsonb
                    where functionid = '60000000-0000-0000-0000-000000000001';

            """,
        )
    ]
