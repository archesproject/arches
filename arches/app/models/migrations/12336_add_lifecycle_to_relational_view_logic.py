from arches.app.models.utils import format_file_into_sql
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("models", "12009_language_single_default_language"),
    ]

    operations = [
        migrations.RunSQL(
            format_file_into_sql(
                "12336__arches_instance_view_update.sql",
                "sql/functions",
            ),
            format_file_into_sql(
                "8770__arches_instance_view_update.sql",
                "sql/functions",
            ),
        ),
    ]
