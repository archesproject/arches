from arches.app.models.utils import format_file_into_sql
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("models", "12009_language_single_default_language"),
    ]

    operations = [
        migrations.RunSQL(
            format_file_into_sql(
                "2025-07-24__12336__arches_instance_view_update.sql",
                "sql/functions/2025",
            ),
            format_file_into_sql(
                "2022-08-05__8770__arches_instance_view_update.sql",
                "sql/functions/2022",
            ),
        ),
    ]
