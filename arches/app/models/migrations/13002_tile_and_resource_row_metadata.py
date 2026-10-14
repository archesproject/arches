from django.db import migrations

import arches.app.models.fields.database_managed_fields

TABLES = (
    ("resource_instances", "resource_instances_id_seq"),
    ("tiles", "tiles_id_seq"),
)

create_sequences = "\n".join(
    f"CREATE SEQUENCE IF NOT EXISTS {sequence} AS bigint;" for _, sequence in TABLES
)
drop_sequences = "\n".join(
    f"DROP SEQUENCE IF EXISTS {sequence};" for _, sequence in TABLES
)

own_sequences = "\n".join(
    f"ALTER SEQUENCE {sequence} OWNED BY {table}.id;" for table, sequence in TABLES
)
disown_sequences = "\n".join(
    f"ALTER SEQUENCE {sequence} OWNED BY NONE;" for _, sequence in TABLES
)

# id, createdtime and updated are owned by the database, regardless of whether
# a row arrives via the ORM, raw SQL (e.g. the ETL loaders), or COPY.
#   INSERT: fill in anything not supplied (explicit values are kept so that
#           dumps/restores and legacy imports round-trip).
#   UPDATE: id and createdtime can never change; updated is bumped only when
#           some other column actually changed, so blind re-saves are no-ops.
create_trigger_function = """
    CREATE OR REPLACE FUNCTION __arches_manage_row_metadata()
    RETURNS trigger AS $$
    BEGIN
        IF TG_OP = 'INSERT' THEN
            NEW.id := COALESCE(NEW.id, nextval(TG_ARGV[0]::regclass));
            NEW.createdtime := COALESCE(NEW.createdtime, statement_timestamp());
            NEW.updated := COALESCE(NEW.updated, statement_timestamp());
            RETURN NEW;
        END IF;

        NEW.id := OLD.id;
        NEW.createdtime := OLD.createdtime;
        NEW.updated := OLD.updated;
        IF NEW IS DISTINCT FROM OLD THEN
            NEW.updated := statement_timestamp();
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
"""
drop_trigger_function = "DROP FUNCTION IF EXISTS __arches_manage_row_metadata();"

create_triggers = "\n".join(f"""
    CREATE TRIGGER __arches_manage_row_metadata_trigger
        BEFORE INSERT OR UPDATE ON {table}
        FOR EACH ROW
        EXECUTE FUNCTION __arches_manage_row_metadata('{sequence}');
    """ for table, sequence in TABLES)
drop_triggers = "\n".join(
    f"DROP TRIGGER IF EXISTS __arches_manage_row_metadata_trigger ON {table};"
    for table, _ in TABLES
)


class Migration(migrations.Migration):

    dependencies = [
        ("models", "13001_spatialview_dbroles"),
    ]

    operations = [
        migrations.RunSQL(create_sequences, drop_sequences),
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
            name="updated",
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
            name="updated",
            field=arches.app.models.fields.database_managed_fields.DatabaseTimestampField(),
        ),
        migrations.RunSQL(own_sequences, disown_sequences),
        migrations.RunSQL(create_trigger_function, drop_trigger_function),
        migrations.RunSQL(create_triggers, drop_triggers),
    ]
