import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "10097_add_editlog_index"),
    ]

    update_staging_function = """
        DROP FUNCTION IF EXISTS __arches_stage_string_data_for_bulk_edit(uuid, uuid, uuid, uuid, uuid[], text, text, text, boolean, integer);
        CREATE OR REPLACE FUNCTION __arches_stage_string_data_for_bulk_edit(
            load_id uuid,
            graph_id uuid,
            node_id uuid,
            module_id uuid,
            resourceinstance_ids uuid[],
            operation text,
            old_text text,
            new_text text,
            language_code text,
            case_insensitive boolean,
            update_limit integer
        )
        RETURNS VOID
        LANGUAGE 'plpgsql'
        AS $$
            DECLARE
                tile_id uuid;
                tile_data jsonb;
                nodegroup_id uuid;
                parenttile_id uuid;
                resourceinstance_id uuid;
                text_replacing_like text;
            BEGIN
                INSERT INTO load_staging (tileid, value, nodegroupid, parenttileid, resourceid, loadid, nodegroup_depth, source_description, operation, passes_validation)
                    SELECT DISTINCT t.tileid, t.tiledata, t.nodegroupid, t.parenttileid, t.resourceinstanceid, load_id, 0, 'bulk_edit', 'update', true
                    FROM tiles t, nodes n
                    WHERE t.nodegroupid = n.nodegroupid
                    AND CASE
                        WHEN graph_id IS NULL THEN true
                        ELSE n.graphid = graph_id
                        END
                    AND CASE
                        WHEN node_id IS NULL THEN n.datatype = 'string'
                        ELSE n.nodeid = node_id
                        END
                    AND CASE
                        WHEN resourceinstance_ids IS NULL THEN true
                        ELSE t.resourceinstanceid = ANY(resourceinstance_ids)
                        END
                    AND CASE operation
                        WHEN 'trim' THEN
                            t.tiledata -> nodeid::text -> language_code ->> 'value' <> TRIM(t.tiledata -> nodeid::text -> language_code ->> 'value')
                        WHEN 'capitalize' THEN
                            t.tiledata -> nodeid::text -> language_code ->> 'value' <> INITCAP(t.tiledata -> nodeid::text -> language_code ->> 'value')
                        WHEN 'capitalize_trim' THEN
                            t.tiledata -> nodeid::text -> language_code ->> 'value' <> TRIM(INITCAP(t.tiledata -> nodeid::text -> language_code ->> 'value'))
                        WHEN 'upper' THEN
                            t.tiledata -> nodeid::text -> language_code ->> 'value' <> UPPER(t.tiledata -> nodeid::text -> language_code ->> 'value')
                        WHEN 'upper_trim' THEN
                            t.tiledata -> nodeid::text -> language_code ->> 'value' <> TRIM(UPPER(t.tiledata -> nodeid::text -> language_code ->> 'value'))
                        WHEN 'lower' THEN
                            t.tiledata -> nodeid::text -> language_code ->> 'value' <> LOWER(t.tiledata -> nodeid::text -> language_code ->> 'value')
                        WHEN 'lower_trim' THEN
                            t.tiledata -> nodeid::text -> language_code ->> 'value' <> TRIM(LOWER(t.tiledata -> nodeid::text -> language_code ->> 'value'))
                        WHEN 'replace_i' THEN
                            t.tiledata -> nodeid::text -> language_code ->> 'value' <> REGEXP_REPLACE(t.tiledata -> nodeid::text -> language_code ->> 'value', old_text, new_text, 'gi')
                        WHEN 'replace' THEN
                            t.tiledata -> nodeid::text -> language_code ->> 'value' <> REGEXP_REPLACE(t.tiledata -> nodeid::text -> language_code ->> 'value', old_text, new_text, 'g')
                        END
                    LIMIT update_limit;
            END;
        $$;
    """

    revert_staging_function = """
        DROP FUNCTION IF EXISTS __arches_stage_string_data_for_bulk_edit(uuid, uuid, uuid, uuid, uuid[], text, text, text, text, boolean, integer);
        CREATE OR REPLACE FUNCTION __arches_stage_string_data_for_bulk_edit(
            load_id uuid,
            graph_id uuid,
            node_id uuid,
            module_id uuid,
            resourceinstance_ids uuid[],
            operation text,
            text_replacing text,
            language_code text,
            case_insensitive boolean,
            update_limit integer
        )
        RETURNS VOID
        LANGUAGE 'plpgsql'
        AS $$
            DECLARE
                tile_id uuid;
                tile_data jsonb;
                nodegroup_id uuid;
                parenttile_id uuid;
                resourceinstance_id uuid;
                text_replacing_like text;
            BEGIN
                IF text_replacing IS NOT NULL THEN
                    text_replacing_like = FORMAT('%%%s%%', text_replacing);
                END IF;
                INSERT INTO load_staging (tileid, value, nodegroupid, parenttileid, resourceid, loadid, nodegroup_depth, source_description, operation, passes_validation)
                    SELECT DISTINCT t.tileid, t.tiledata, t.nodegroupid, t.parenttileid, t.resourceinstanceid, load_id, 0, 'bulk_edit', 'update', true
                    FROM tiles t, nodes n
                    WHERE t.nodegroupid = n.nodegroupid
                    AND CASE
                        WHEN graph_id IS NULL THEN true
                        ELSE n.graphid = graph_id
                        END
                    AND CASE
                        WHEN node_id IS NULL THEN n.datatype = 'string'
                        ELSE n.nodeid = node_id
                        END
                    AND CASE
                        WHEN resourceinstance_ids IS NULL THEN true
                        ELSE t.resourceinstanceid = ANY(resourceinstance_ids)
                        END
                    AND CASE
                        WHEN text_replacing IS NULL THEN
                            CASE operation
                                WHEN 'trim' THEN
                                    t.tiledata -> nodeid::text -> language_code ->> 'value' <> TRIM(t.tiledata -> nodeid::text -> language_code ->> 'value')
                                WHEN 'capitalize' THEN
                                    t.tiledata -> nodeid::text -> language_code ->> 'value' <> INITCAP(t.tiledata -> nodeid::text -> language_code ->> 'value')
                                WHEN 'capitalize_trim' THEN
                                    t.tiledata -> nodeid::text -> language_code ->> 'value' <> TRIM(INITCAP(t.tiledata -> nodeid::text -> language_code ->> 'value'))
                                WHEN 'upper' THEN
                                    t.tiledata -> nodeid::text -> language_code ->> 'value' <> UPPER(t.tiledata -> nodeid::text -> language_code ->> 'value')
                                WHEN 'upper_trim' THEN
                                    t.tiledata -> nodeid::text -> language_code ->> 'value' <> TRIM(UPPER(t.tiledata -> nodeid::text -> language_code ->> 'value'))
                                WHEN 'lower' THEN
                                    t.tiledata -> nodeid::text -> language_code ->> 'value' <> LOWER(t.tiledata -> nodeid::text -> language_code ->> 'value')
                                WHEN 'lower_trim' THEN
                                    t.tiledata -> nodeid::text -> language_code ->> 'value' <> TRIM(LOWER(t.tiledata -> nodeid::text -> language_code ->> 'value'))
                            END
                        WHEN language_code IS NOT NULL AND case_insensitive THEN
                            t.tiledata -> nodeid::text -> language_code ->> 'value' ilike text_replacing_like
                        WHEN language_code IS NOT NULL AND NOT case_insensitive THEN
                            t.tiledata -> nodeid::text -> language_code ->> 'value' like text_replacing_like
                        WHEN language_code IS NULL AND case_insensitive THEN
                            t.tiledata::text ilike text_replacing_like
                        WHEN language_code IS NULL AND NOT case_insensitive THEN
                            t.tiledata::text like text_replacing_like
                        END
                    LIMIT update_limit;
            END;
        $$;
    """

    update_editing_function = """
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
                                                to_jsonb(REGEXP_REPLACE(updated_value -> language_code ->> 'value', old_text, new_text, 'g'))
                                            WHEN 'replace_i' THEN
                                                to_jsonb(REGEXP_REPLACE(updated_value -> language_code ->> 'value', old_text, new_text, 'gi'))
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

    operations = [
        migrations.RunSQL(
            update_staging_function,
            revert_staging_function,
        ),
        migrations.RunSQL(
            update_editing_function,
            revert_editing_function,
        ),
    ]
