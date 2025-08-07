from django.db import migrations


UPDATE_LOAD_STAGING_GET_TILE_ERRORS_FUNCTION = f"""
    CREATE OR REPLACE FUNCTION public.__arches_load_staging_get_tile_errors(json_obj jsonb)
    RETURNS text
    LANGUAGE plpgsql AS

    $func$
    DECLARE
        _key   text;
        _value jsonb;
        _result text;
        _note text;

    BEGIN
        FOR _key, _value IN
            SELECT * FROM jsonb_each_text($1)
        LOOP
            IF _value ->> 'valid' = 'false' THEN
                IF _value ->> 'notes' IS NULL THEN
                    _note = 'unspecified error';
                END IF;
                -- we could add the nodeid (_key), but let's not be verbose just yet
                IF _result IS NULL THEN
                _result := _value ->> 'notes';
                ELSE
                _result := '|' || (_value ->> 'notes');
                END IF;
            END IF;
        END LOOP;
        RETURN _result;
    END;
    $func$;
"""


class Migration(migrations.Migration):
    dependencies = [
        ("models", "12284_resource_fields_read_only"),
    ]

    operations = [
        migrations.RunSQL(
            UPDATE_LOAD_STAGING_GET_TILE_ERRORS_FUNCTION,
            migrations.RunSQL.noop,  # No reverse operation needed
        ),
    ]
