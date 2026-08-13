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
    SQLItem(
        "__arches_check_tile_cardinality_violation_for_load",
        format_file_into_sql(
            "__arches_check_tile_cardinality_violation_for_load.sql", "sql/procedures"
        ),
        reverse_sql="drop procedure __arches_check_tile_cardinality_violation_for_load;",
        replace=True,
    ),
    SQLItem(
        "__arches_slugify",
        format_file_into_sql("__arches_slugify.sql", "sql/functions"),
        reverse_sql="drop function __arches_slugify;",
        replace=True,
    ),
    SQLItem(
        "__arches_get_node_value_sql",
        format_file_into_sql("__arches_get_node_value_sql.sql", "sql/functions"),
        reverse_sql="drop function __arches_get_node_value_sql;",
        replace=True,
    ),
    SQLItem(
        "__arches_create_nodegroup_view",
        format_file_into_sql("__arches_create_nodegroup_view.sql", "sql/functions"),
        reverse_sql="drop function __arches_create_nodegroup_view;",
        dependencies=[("models", "__arches_get_node_value_sql")],
        replace=True,
    ),
    SQLItem(
        "__arches_create_branch_views",
        format_file_into_sql("__arches_create_branch_views.sql", "sql/functions"),
        reverse_sql="drop function __arches_create_branch_views;",
        dependencies=[("models", "__arches_create_nodegroup_view")],
        replace=True,
    ),
    SQLItem(
        "__arches_create_resource_model_views",
        format_file_into_sql(
            "__arches_create_resource_model_views.sql", "sql/functions"
        ),
        reverse_sql="drop function __arches_create_resource_model_views;",
        dependencies=[
            ("models", "__arches_slugify"),
            ("models", "__arches_create_branch_views"),
        ],
        replace=True,
    ),
]
