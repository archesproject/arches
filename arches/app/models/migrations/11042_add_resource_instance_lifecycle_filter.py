import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "11042_add_resource_instance_lifecycle_triggers"),
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
                "sortorder",
                "enabled")
            values (
                '9e40969b-78c2-40b8-898b-c29265050e2f',
                'Lifecycle State Filter',
                '',
                'lifecycle_state_filter.py',
                'LifecycleStateFilter',
                '',
                'views/components/search/lifecycle-state-filter',
                'lifecycle-state-filter',
                0,
                true);
            """,
        ),
    ]
