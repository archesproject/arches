from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "4670_adds_map_card"),
    ]

    operations = [
        migrations.RunSQL(
            """
            delete from plugins where pluginid = 'f477b613-552f-22f0-0e38-d5c412cbbc0e';
            """,
            """
            insert into plugins (
                    pluginid,
                    name,
                    icon,
                    component,
                    componentname,
                    config)
                values (
                    'f477b613-552f-22f0-0e38-d5c412cbbc0e',
                    'Select Workflow',
                    'fa fa-magic',
                    'views/components/plugins/workflow-select',
                    'workflow-select-plugin',
                    '{}'
            );
            """,
        )
    ]
