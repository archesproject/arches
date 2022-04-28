from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "7262_report_template_data_fetch_bool"),
    ]

    operations = [
        migrations.RunSQL(
            """
            INSERT INTO public.functions(
                functionid, 
                functiontype, 
                name, 
                description, 
                defaultconfig, 
                modulename, 
                classname, 
                component)
                VALUES (
                    '3558cdb8-0bc1-440f-ae2b-295b58729e8e', 
                    '', 
                    'Resource Edit Tracker',
                    'Can be used to identify a function that can be used to track edits to resources.', 
                    '{
                        "triggering_nodegroups": [], 
                        "selected_nodes": [], 
                        "modulename": ""
                    }',  
                    'resource_edits.py', 
                    'ResourceEdits', 
                    'views/components/functions/resource-edits'
                );
            """,
            """
            DELETE FROM public.functions
            WHERE functionid = '3558cdb8-0bc1-440f-ae2b-295b58729e8e';
            """,
        )
    ]
