# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("models", "4375_add_unique_constraint_models"),
    ]

    operations = [
        migrations.RunSQL(
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
            """
            delete from plugins where pluginid = 'f477b613-552f-22f0-0e38-d5c412cbbc0e';
            """,
        )
    ]
