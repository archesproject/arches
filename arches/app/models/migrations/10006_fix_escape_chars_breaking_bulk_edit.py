import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "9944_update_refresh_relationship_function"),
    ]

    update_editing_function = """
        DROP FUNCTION IF EXISTS __arches_edit_staged_data(uuid,uuid,uuid,text,text,text,text);
        CREATE OR REPLACE FUNCTION __arches_edit_staged_string_data(
            load_id uuid,
            graph_id uuid,
            node_id uuid,
            language_code text,
            operation text,
            old_text text,
            new_text text
        )
        RETURNS VOID
        LANGUAGE 'plpgsql'
        AS $$
            DECLARE
                node_ids uuid[];
                language_codes text[];
                tile_id uuid;
                tile_data jsonb;
                nodegroup_id uuid;
                parenttile_id uuid;
                resourceinstance_id uuid;
                data_type text;
                transform_sql text;
                updated_staged_data jsonb;
                updated_value jsonb;
                staged_record record;
                _key text;
                _value text;
            BEGIN
                IF node_id IS NULL THEN
                    node_ids := ARRAY(
                        SELECT nodeid
                        FROM nodes
                        WHERE datatype = 'string'
                        AND graphid = graph_id
                    );
                ELSE
                    node_ids = ARRAY[node_id];
                END IF;

                IF language_code IS NULL THEN
                    language_codes := ARRAY(SELECT code FROM languages);
                ELSE
                    language_codes = ARRAY[language_code];
                END IF;

                FOR staged_record IN (SELECT value, tileid FROM load_staging WHERE loadid = load_id) LOOP
                    updated_staged_data = '{}'::jsonb;
                    FOR _key, _value IN SELECT * FROM jsonb_each(staged_record.value) LOOP
                        SELECT datatype INTO data_type FROM nodes WHERE nodeid = _key::uuid;
                        updated_value = _value::jsonb;
                        IF _key::uuid = ANY(node_ids) THEN
                            IF data_type = 'string' THEN
                                FOREACH language_code IN ARRAY language_codes LOOP
                                    updated_value = jsonb_set(
                                        updated_value,
                                        FORMAT('{%s, "value"}', language_code)::text[],
                                        CASE operation
                                            WHEN 'replace' THEN
                                                to_jsonb(REPLACE(updated_value -> language_code ->> 'value', old_text, new_text))
                                            WHEN 'replace_i' THEN
                                                to_jsonb(REGEXP_REPLACE(updated_value -> language_code ->> 'value', old_text, new_text, 'i'))
                                            WHEN 'trim' THEN
                                                to_jsonb(TRIM(updated_value -> language_code ->> 'value'))
                                            WHEN 'capitalize' THEN
                                                to_jsonb(INITCAP(updated_value -> language_code ->> 'value'))
                                            WHEN 'capitalize_trim' THEN
                                                to_jsonb(TRIM(INITCAP(updated_value -> language_code ->> 'value')))
                                            WHEN 'upper' THEN
                                                to_jsonb(UPPER(updated_value -> language_code ->> 'value'))
                                            WHEN 'upper_trim' THEN
                                                to_jsonb(TRIM(UPPER(updated_value -> language_code ->> 'value')))
                                            WHEN 'lower' THEN
                                                to_jsonb(LOWER(updated_value -> language_code ->> 'value'))
                                            WHEN 'lower_trim' THEN
                                                to_jsonb(TRIM(LOWER(updated_value -> language_code ->> 'value')))
                                            ELSE
                                                to_jsonb(updated_value -> language_code ->> 'value')
                                        END
                                    );
                                -- ELSEIF for other datatypes
                                END LOOP;
                            END IF;
                        END IF;
                        updated_staged_data = jsonb_set(
                            updated_staged_data,
                            FORMAT('{%s}', _key)::text[],
                            jsonb_build_object(
                                'notes', '',
                                'valid', true,
                                'source', 'bulk_edit',
                                'datatype', data_type,
                                'value', updated_value
                            ),
                            true
                        );
                        UPDATE load_staging
                        SET value = updated_staged_data
                        WHERE loadid = load_id AND tileid = staged_record.tileid;
                    END LOOP;
                END LOOP;
            END;
        $$;
    """

    revert_editing_function = """
        DROP FUNCTION IF EXISTS __arches_edit_staged_data(uuid,uuid,uuid,text,text,text,text);
        CREATE OR REPLACE FUNCTION __arches_edit_staged_string_data(
            load_id uuid,
            graph_id uuid,
            node_id uuid,
            language_code text,
            operation text,
            old_text text,
            new_text text
        )
        RETURNS VOID
        LANGUAGE 'plpgsql'
        AS $$
            DECLARE
                node_ids uuid[];
                language_codes text[];
                tile_id uuid;
                tile_data jsonb;
                nodegroup_id uuid;
                parenttile_id uuid;
                resourceinstance_id uuid;
                data_type text;
                transform_sql text;
                updated_staged_data jsonb;
                updated_value jsonb;
                staged_record record;
                _key text;
                _value text;
            BEGIN
                IF node_id IS NULL THEN
                    node_ids := ARRAY(
                        SELECT nodeid
                        FROM nodes
                        WHERE datatype = 'string'
                        AND graphid = graph_id
                    );
                ELSE
                    node_ids = ARRAY[node_id];
                END IF;

                IF language_code IS NULL THEN
                    language_codes := ARRAY(SELECT code FROM languages);
                ELSE
                    language_codes = ARRAY[language_code];
                END IF;

                FOR staged_record IN (SELECT value, tileid FROM load_staging WHERE loadid = load_id) LOOP
                    updated_staged_data = '{}'::jsonb;
                    FOR _key, _value IN SELECT * FROM jsonb_each(staged_record.value) LOOP
                        SELECT datatype INTO data_type FROM nodes WHERE nodeid = _key::uuid;
                        updated_value = _value::jsonb;
                        IF _key::uuid = ANY(node_ids) THEN
                            IF data_type = 'string' THEN
                                FOREACH language_code IN ARRAY language_codes LOOP
                                    updated_value = jsonb_set(
                                        updated_value,
                                        FORMAT('{%s, "value"}', language_code)::text[],
                                        CASE operation
                                            WHEN 'replace' THEN
                                                FORMAT('"%s"', REPLACE(updated_value -> language_code ->> 'value', old_text, new_text))::jsonb
                                            WHEN 'replace_i' THEN
                                                FORMAT('"%s"', REGEXP_REPLACE(updated_value -> language_code ->> 'value', old_text, new_text, 'i'))::jsonb
                                            WHEN 'trim' THEN
                                                FORMAT('"%s"', TRIM(updated_value -> language_code ->> 'value'))::jsonb
                                            WHEN 'capitalize' THEN
                                                FORMAT('"%s"', INITCAP(updated_value -> language_code ->> 'value'))::jsonb
                                            WHEN 'capitalize_trim' THEN
                                                FORMAT('"%s"', TRIM(INITCAP(updated_value -> language_code ->> 'value')))::jsonb
                                            WHEN 'upper' THEN
                                                FORMAT('"%s"', UPPER(updated_value -> language_code ->> 'value'))::jsonb
                                            WHEN 'upper_trim' THEN
                                                FORMAT('"%s"', TRIM(UPPER(updated_value -> language_code ->> 'value')))::jsonb
                                            WHEN 'lower' THEN
                                                FORMAT('"%s"', LOWER(updated_value -> language_code ->> 'value'))::jsonb
                                            WHEN 'lower_trim' THEN
                                                FORMAT('"%s"', TRIM(LOWER(updated_value -> language_code ->> 'value')))::jsonb
                                            ELSE
                                                FORMAT('"%s"', updated_value -> language_code ->> 'value')::jsonb
                                        END
                                    );
                                -- ELSEIF for other datatypes
                                END LOOP;
                            END IF;
                        END IF;
                        updated_staged_data = jsonb_set(
                            updated_staged_data,
                            FORMAT('{%s}', _key)::text[],
                            jsonb_build_object(
                                'notes', '',
                                'valid', true,
                                'source', 'bulk_edit',
                                'datatype', data_type,
                                'value', updated_value
                            ),
                            true
                        );
                        UPDATE load_staging
                        SET value = updated_staged_data
                        WHERE loadid = load_id AND tileid = staged_record.tileid;
                    END LOOP;
                END LOOP;
            END;
        $$;
    """

    operations = [
        migrations.RunSQL(
            update_editing_function,
            revert_editing_function,
        ),
    ]
