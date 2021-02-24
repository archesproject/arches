# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("models", "6979_manifest_manager"),
    ]

    sql = """
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
            '6a2fe122-de54-4e44-8e93-b6a0cda7955c',
            'Sort',
            '',
            'sort_results.py',
            'SortResults',
            '',
            'views/components/search/sort-results',
            'sort-results',
            0,
            true);
        """
    reverse_sql = """
        delete from search_component where searchcomponentid = '6a2fe122-de54-4e44-8e93-b6a0cda7955c';
        """

    operations = [
        migrations.RunSQL(
            sql,
            reverse_sql,
        )
    ]
