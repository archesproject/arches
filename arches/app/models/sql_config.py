from django.db import migrations
from django_migrate_sql.config import SQLItem
from arches.app.models.utils import format_file_into_sql


sql_items = [
    SQLItem(
        "__arches_instance_view_update",
        format_file_into_sql("__arches_instance_view_update.sql", "sql/functions"),
        reverse_sql="drop function __arches_instance_view_update;",
        replace=True,
    ),
    SQLItem(
        "__arches_load_staging_get_tile_errors",
        format_file_into_sql(
            "__arches_load_staging_get_tile_errors.sql", "sql/functions"
        ),
        reverse_sql="drop function __arches_load_staging_get_tile_errors;",
    ),
    SQLItem(
        "__arches_get_json_data_for_view",
        format_file_into_sql("__arches_get_json_data_for_view.sql", "sql/functions"),
        reverse_sql="drop function __arches_get_json_data_for_view;",
        replace=True,
    ),
    SQLItem(
        "__arches_get_nodevalue_label",
        format_file_into_sql("__arches_get_nodevalue_label.sql", "sql/functions"),
        reverse_sql="drop function __arches_get_nodevalue_label;",
        replace=True,
    ),
    SQLItem(
        "__arches_get_node_display_value",
        format_file_into_sql("__arches_get_node_display_value.sql", "sql/functions"),
        reverse_sql="drop function __arches_get_node_display_value;",
        replace=True,
    ),
]
