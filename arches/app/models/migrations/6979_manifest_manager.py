# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("models", "6843_manifest_file_model"),
    ]

    sql = """
        insert into plugins (
            pluginid,
            name,
            icon,
            component,
            componentname,
            config,
            slug,
            sortorder)
        values (
            '6f707d86-d49c-4ece-9883-8cbb2ecda1b5',
            'Image Service Manager',
            'fa fa-image',
            'views/components/plugins/manifest-manager',
            'manifest-manager',
            '{"show": false}',
            'image-service-manager',
            1);
        """
    reverse_sql = """
        delete from plugins where pluginid = '6f707d86-d49c-4ece-9883-8cbb2ecda1b5';
        """

    operations = [
        migrations.RunSQL(
            sql,
            reverse_sql,
        )
    ]
