Adding an initial migration for existing database functions
===========================================================

- Recover the old function from the database.
- Paste it into a new file under arches/app/models/migrations/sql/functions.
- Add a SQLItem() in sql_config.py like::
```python
    SQLItem(
        "__arches_instance_view_update",
        format_file_into_sql("__arches_instance_view_update.sql", "sql/functions"),
        reverse_sql="drop function __arches_instance_view_update;",
        replace=True,
    ),
```
- manage.py makemigrations --name <description>
- Edit the migration number to follow the Arches convention of using issue numbers.
- Edit the migration file to treat the CreateSQL operation as a state-only operation,
  since the function already exists in the database.::
```python
    operations = [
        migrations.operations.special.SeparateDatabaseAndState(
            state_operations=[
                django_migrate_sql.operations.CreateSQL(
                    name="__arches_instance_view_update",
                    sql="\nCREATE OR REPLACE FUNCTION ...
                    reverse_sql="drop function __arches_instance_view_update;",
                ),
            ],
        ),
    ]
```
- Create a commit.
- Make your changes to the function SQL file.
- manage.py makemigrations
- Move the operation from the second migration into the end of previous migration (as
a top-level operation) and delete the second migration::
```python
    operations = [
        migrations.operations.special.SeparateDatabaseAndState(
            state_operations=[
                django_migrate_sql.operations.CreateSQL(
                    name="__arches_instance_view_update",
                    sql="\nCREATE OR REPLACE FUNCTION ...
                    reverse_sql="drop function __arches_instance_view_update;",
                ),
            ],
        ),
        django_migrate_sql.operations.AlterSQL(
            name="__arches_instance_view_update",
            sql="\ncreate or replace function __arches_instance_view_update() ...,
            reverse_sql="\nCREATE OR REPLACE FUNCTION public.__arches_instance_view_update()...,
            state_reverse_sql="drop function __arches_instance_view_update;",
        ),
    ]
