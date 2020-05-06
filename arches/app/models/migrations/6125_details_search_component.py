from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("models", "2724_instance_permissions"),
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
                'f5986dae-8b01-11ea-b65a-77903936669c',
                'Details',
                'fa fa-info-circle',
                '',
                '',
                'filter',
                'views/components/search/search-result-details',
                'search-result-details',
                4,
                true);
            """,
            """
            delete from search_component
                where searchcomponentid = 'f5986dae-8b01-11ea-b65a-77903936669c';
            """,
        ),
    ]
