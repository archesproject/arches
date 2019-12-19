# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("models", "5616_search_export_history"),
    ]

    operations = [
        migrations.RunSQL(
            """
            update nodes set name = 'SEARCH_EXPORT_LIMIT' WHERE nodeid = 'd0987ec0-fad8-11e6-aad3-6c4008b05c4c';
            """,
            """
            update nodes set name = 'SEARCH_EXPORT_ITEMS_PER_PAGE' WHERE nodeid = 'd0987ec0-fad8-11e6-aad3-6c4008b05c4c';
            """,
        )
    ]
