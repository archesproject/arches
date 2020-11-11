# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("models", "6759_fn_unique_component")]

    sql = """
    UPDATE widgets SET defaultconfig = jsonb_set(defaultconfig, '{uneditable}', 'false')
    WHERE widgetid IN ('10000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000008');
    UPDATE cards_x_nodes_x_widgets SET config = jsonb_set(config, '{uneditable}', 'false')
    WHERE widgetid IN ('10000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000008');
    """

    reverse_sql = (
        """
    UPDATE widgets SET defaultconfig = defaultconfig - 'uneditable'
    WHERE widgetid IN ('10000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000008');
    UPDATE cards_x_nodes_x_widgets SET config = config - 'uneditable'
    WHERE widgetid IN ('10000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000008');
    """,
    )

    operations = [
        migrations.RunSQL(
            sql,
            reverse_sql,
        ),
    ]
