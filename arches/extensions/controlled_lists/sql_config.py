from django_migrate_sql.config import SQLItem
from pathlib import Path


def format_file_into_sql(file: str, sql_dir: str):
    sql_file = Path(__file__).parent / sql_dir / file
    sql_string = ""
    with open(sql_file) as file:
        sql_string = sql_string + "\n" + file.read()
    return sql_string


sql_items = [
    SQLItem(
        "__arches_migrate_collections_to_clm",
        format_file_into_sql("__arches_migrate_collections_to_clm.sql", "sql"),
        reverse_sql="drop function __arches_migrate_collections_to_clm;",
        replace=True,
    ),
]
