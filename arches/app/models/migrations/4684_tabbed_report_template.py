# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("models", "4661_workflowselect_plugin"),
    ]

    operations = [
        migrations.RunSQL(
            """
        insert into report_templates (
                templateid,
                name,
                description,
                component,
                componentname,
                defaultconfig)
            values (
                '50000000-0000-0000-0000-000000000004',
                'Tabbed Template',
                'Tabbed',
                'reports/tabbed',
                'tabbed-report',
                '{
                "tabs": [
                    {
                        "icon": "fa-tags",
                        "name": "Consultation Summary Report",
                        "nodegroup_ids": ["04723f59-53f2-11e9-b091-dca90488358a",
                        "17c07f07-53f5-11e9-9c94-dca90488358a","2c1e9d07-53f4-11e9-8b56-dca90488358a",
                        "3c79d87a-53f2-11e9-a14e-dca90488358a","520b30dc-53f5-11e9-b79d-dca90488358a",
                        "5b70438f-53f4-11e9-81ef-dca90488358a","80be5b5c-5675-11e9-b68d-dca90488358a",
                        "9739f81c-53f4-11e9-9b39-dca90488358a","9dc86b0c-6c48-11e9-8cbe-dca90488358a",
                        "b979d03d-53f2-11e9-91e4-dca90488358a","daf936f5-540a-11e9-8a83-dca90488358a",
                        "f34ebbd4-53f3-11e9-b649-dca90488358a"]
                    },
                    {
                        "icon": "fa-map-marker",
                        "name": "Location Information",
                        "nodegroup_ids": ["09cb95f5-53d8-11e9-aa83-dca90488358a",
                        "138478e1-6d23-11e9-808c-dca90488358a","2c82277d-53db-11e9-934b-dca90488358a",
                        "63cdcf0f-53da-11e9-8340-dca90488358a","c5f909b5-53c7-11e9-a3ac-dca90488358a",
                        "e19fe3a1-6d22-11e9-98bf-dca90488358a","e857704a-53d8-11e9-b05a-dca90488358a",
                        "eafced66-53d8-11e9-a4e2-dca90488358a"]
                    },
                    {
                        "icon": "fa-clipboard",
                        "name": "Site Visits",
                        "nodegroup_ids": ["18ae6b57-6c48-11e9-83c1-dca90488358a",
                        "4451d38f-6c47-11e9-83e0-dca90488358a","571dba97-6c47-11e9-8bed-dca90488358a",
                        "7a97945c-6c46-11e9-ae4b-dca90488358a","9809201e-6c46-11e9-a918-dca90488358a",
                        "b21ef6c0-6c46-11e9-9205-dca90488358a","c56a5233-6d28-11e9-aa0d-dca90488358a",
                        "cb717640-6c46-11e9-9b10-dca90488358a","f57ec302-6c46-11e9-93b3-dca90488358a"]
                    },
                    {
                        "icon": "fa-comment-o",
                        "name": "Communications",
                        "nodegroup_ids": ["0b0cf4b0-6c4b-11e9-8ec5-dca90488358a",
                        "23e1ac91-6c4b-11e9-8641-dca90488358a","395a96a3-6c4b-11e9-b7d9-dca90488358a",
                        "6fda4838-6d1e-11e9-b3d5-dca90488358a","70fd3940-6d1f-11e9-87dd-dca90488358a",
                        "8b171540-6d1e-11e9-ac56-dca90488358a","a5901911-6d1e-11e9-8674-dca90488358a",
                        "fcb84b0f-6d1e-11e9-881a-dca90488358a"]
                    },
                    {
                        "icon": "fa-code-fork",
                        "name": "Related Applications",
                        "nodegroup_ids": ["2c82277d-53db-11e9-934b-dca90488358a"]
                    }
                ]
            }'
            );
            """,
            """
            delete from report_templates where templateid = '50000000-0000-0000-0000-000000000004';
            """,
        )
    ]
