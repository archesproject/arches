import django_migrate_sql.operations
from django.db import migrations

from arches.app.models.utils import format_file_into_sql


class Migration(migrations.Migration):

    dependencies = [
        ("models", "12779_add_multicard_resource_descriptor"),
    ]

    operations = [
        # A new function, so a plain CreateSQL: it executes the SQL and records
        # the item in migration state. The SeparateDatabaseAndState dance in
        # 12586/12343 is only for adopting functions that predate migrate_sql.
        django_migrate_sql.operations.CreateSQL(
            name="__arches_refresh_transaction_resource_relationships",
            sql=format_file_into_sql(
                "__arches_refresh_transaction_resource_relationships.sql",
                "sql/functions",
            ),
            reverse_sql=(
                "drop function __arches_refresh_transaction_resource_relationships;"
            ),
        ),
    ]
