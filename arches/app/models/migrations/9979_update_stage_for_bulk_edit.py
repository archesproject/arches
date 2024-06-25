from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("models", "10006_fix_escape_chars_breaking_bulk_edit"),
    ]

    update_staging_function = """
        DROP FUNCTION IF EXISTS __arches_stage_string_data_for_bulk_edit(uuid, uuid, uuid, uuid, uuid[], text, text, boolean);
        CREATE OR REPLACE FUNCTION __arches_stage_string_data_for_bulk_edit(
            load_id uuid,
            graph_id uuid,
            node_id uuid,
            module_id uuid,
            resourceinstance_ids uuid[],
            operation text,
            text_replacing text,
            language_code text,
            case_insensitive boolean
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
                        END;
            END;
        $$;
    """

    revert_staging_function = """
        DROP FUNCTION IF EXISTS __arches_stage_string_data_for_bulk_edit(uuid, uuid, uuid, uuid, uuid[], text, text, text, boolean);
        CREATE OR REPLACE FUNCTION __arches_stage_string_data_for_bulk_edit(
            load_id uuid,
            graph_id uuid,
            node_id uuid,
            module_id uuid,
            resourceinstance_ids uuid[],
            text_replacing text,
            language_code text,
            case_insensitive boolean
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
                        WHEN text_replacing IS NULL
                            THEN true
                        WHEN language_code IS NOT NULL AND case_insensitive
                            THEN t.tiledata -> nodeid::text -> language_code ->> 'value' ilike text_replacing_like
                        WHEN language_code IS NOT NULL AND NOT case_insensitive
                            THEN t.tiledata -> nodeid::text -> language_code ->> 'value' like text_replacing_like
                        WHEN language_code IS NULL AND case_insensitive
                            THEN t.tiledata::text ilike text_replacing_like
                        WHEN language_code IS NULL AND NOT case_insensitive
                            THEN t.tiledata::text like text_replacing_like
                        END;
            END;
        $$;
    """

    operations = [
        migrations.RunSQL(
            update_staging_function,
            revert_staging_function,
        ),
    ]
