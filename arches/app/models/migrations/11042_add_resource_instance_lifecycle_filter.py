from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("models", "11042_add_resource_instance_lifecycle"),
    ]

    operations = [
        migrations.RunSQL(
            """
            insert into search_component (
                "searchcomponentid",
                "name",
                "icon",
                "modulename",
                "classname",
                "type",
                "componentpath",
                "componentname",
                "config"
            )
            values (
                '9e40969b-78c2-40b8-898b-c29265050e2f',
                'Lifecycle State Filter',
                '',
                'lifecycle_state_filter.py',
                'LifecycleStateFilter',
                '',
                'views/components/search/lifecycle-state-filter',
                'lifecycle-state-filter',
                '{}'
            );
            """,
            """
            delete from search_component where searchcomponentid = '9e40969b-78c2-40b8-898b-c29265050e2f';
            """,
        ),
    ]
