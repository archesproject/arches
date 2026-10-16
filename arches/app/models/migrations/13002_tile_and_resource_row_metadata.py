import django_migrate_sql.operations
from django.db import migrations

import arches.app.models.fields.database_managed_fields


class Migration(migrations.Migration):

    dependencies = [
        ("models", "12751_widget_uneditable_config"),
    ]

    operations = [
        # The id columns' defaults reference these, so they come first.
        django_migrate_sql.operations.CreateSQL(
            name="resource_instances_id_seq",
            sql="\ncreate sequence if not exists resource_instances_id_seq as bigint;\n",
            reverse_sql="drop sequence if exists resource_instances_id_seq;",
        ),
        django_migrate_sql.operations.CreateSQL(
            name="tiles_id_seq",
            sql="\ncreate sequence if not exists tiles_id_seq as bigint;\n",
            reverse_sql="drop sequence if exists tiles_id_seq;",
        ),
        migrations.AddField(
            model_name="resourceinstance",
            name="id",
            field=arches.app.models.fields.database_managed_fields.NonPrimaryIdentityField(
                sequence_name="resource_instances_id_seq"
            ),
        ),
        migrations.AlterField(
            model_name="resourceinstance",
            name="createdtime",
            field=arches.app.models.fields.database_managed_fields.DatabaseTimestampField(),
        ),
        migrations.AddField(
            model_name="resourceinstance",
            name="last_updated",
            field=arches.app.models.fields.database_managed_fields.DatabaseTimestampField(),
        ),
        migrations.AddField(
            model_name="tilemodel",
            name="id",
            field=arches.app.models.fields.database_managed_fields.NonPrimaryIdentityField(
                sequence_name="tiles_id_seq"
            ),
        ),
        migrations.AddField(
            model_name="tilemodel",
            name="createdtime",
            field=arches.app.models.fields.database_managed_fields.DatabaseTimestampField(),
        ),
        migrations.AddField(
            model_name="tilemodel",
            name="last_updated",
            field=arches.app.models.fields.database_managed_fields.DatabaseTimestampField(),
        ),
        django_migrate_sql.operations.CreateSQL(
            name="__arches_manage_row_metadata",
            sql="\n-- id, createdtime and last_updated are owned by the database, regardless of\n-- whether a row arrives via the ORM, raw SQL (e.g. the ETL loaders), or COPY.\n--   INSERT: always assigned here; any supplied values are discarded, so ids\n--           stay in insertion order (keyset paging relies on it) and\n--           timestamps can't be backdated. Loads that must keep original\n--           values (e.g. pg_restore --data-only, historical migrations) need\n--           the trigger bypassed (session_replication_role = replica or\n--           ALTER TABLE ... DISABLE TRIGGER), followed by\n--           `SELECT setval('tiles_id_seq', (SELECT max(id) FROM tiles));`\n--   UPDATE: id and createdtime can never change; last_updated is bumped only\n--           when some other column actually changed, so blind re-saves are\n--           no-ops.\n-- TG_ARGV[0] is the sequence that supplies the table's ids.\ncreate or replace function __arches_manage_row_metadata()\nreturns trigger as $$\nbegin\n    if tg_op = 'INSERT' then\n        new.id := nextval(tg_argv[0]::regclass);\n        new.createdtime := statement_timestamp();\n        new.last_updated := statement_timestamp();\n        return new;\n    end if;\n\n    new.id := old.id;\n    new.createdtime := old.createdtime;\n    new.last_updated := old.last_updated;\n    if new is distinct from old then\n        new.last_updated := statement_timestamp();\n    end if;\n    return new;\nend;\n$$ language plpgsql;\n",
            reverse_sql="drop function __arches_manage_row_metadata;",
        ),
        django_migrate_sql.operations.CreateSQL(
            name="__arches_manage_row_metadata_trigger",
            sql="\n-- See __arches_manage_row_metadata(); each table passes its own id sequence.\ncreate trigger __arches_manage_row_metadata_trigger\n    before insert or update on resource_instances\n    for each row\n    execute function __arches_manage_row_metadata('resource_instances_id_seq');\n\ncreate trigger __arches_manage_row_metadata_trigger\n    before insert or update on tiles\n    for each row\n    execute function __arches_manage_row_metadata('tiles_id_seq');\n",
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
