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
        "__arches_create_spatial_view",
        format_file_into_sql("__arches_create_spatial_view.sql", "sql/functions"),
        reverse_sql="drop function __arches_create_spatial_view;",
        replace=True,
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
        "__arches_refresh_transaction_resource_relationships",
        format_file_into_sql(
            "__arches_refresh_transaction_resource_relationships.sql", "sql/functions"
        ),
        reverse_sql="drop function __arches_refresh_transaction_resource_relationships;",
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
    # Sequences are replace=True: dropping one to recreate it would fail
    # while the id column's default still references it.
    SQLItem(
        "resource_instances_id_seq",
        format_file_into_sql("resource_instances_id_seq.sql", "sql/sequences"),
        reverse_sql="drop sequence if exists resource_instances_id_seq;",
        replace=True,
    ),
    SQLItem(
        "tiles_id_seq",
        format_file_into_sql("tiles_id_seq.sql", "sql/sequences"),
        reverse_sql="drop sequence if exists tiles_id_seq;",
        replace=True,
    ),
    SQLItem(
        "__arches_manage_row_metadata",
        format_file_into_sql("__arches_manage_row_metadata.sql", "sql/functions"),
        reverse_sql="drop function __arches_manage_row_metadata;",
        replace=True,
    ),
    # Not replace=True: CREATE TRIGGER has no OR REPLACE before PostgreSQL 14,
    # so changes drop (reverse_sql) and recreate the triggers.
    SQLItem(
        "__arches_manage_row_metadata_trigger",
        format_file_into_sql(
            "__arches_manage_row_metadata_trigger.sql", "sql/triggers"
        ),
        reverse_sql=(
            "drop trigger if exists __arches_manage_row_metadata_trigger"
            " on resource_instances;"
            "drop trigger if exists __arches_manage_row_metadata_trigger on tiles;"
        ),
        dependencies=[
            ("models", "__arches_manage_row_metadata"),
            ("models", "resource_instances_id_seq"),
            ("models", "tiles_id_seq"),
        ],
    ),
]
