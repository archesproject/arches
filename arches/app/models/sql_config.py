from django_migrate_sql.config import SQLItem

from arches.app.models.utils import format_file_into_sql


sql_items = [
    SQLItem(
        "__arches_instance_view_update",
        format_file_into_sql("arches_instance_view_update.sql", "sql/functions"),
        reverse_sql="drop function __arches_instance_view_update;",
    ),
]
