from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("models", "8974_rr_load_performance_v2"),
    ]

    add_bulk_data_editor = """
        insert into etl_modules (
            etlmoduleid,
            name,
            description,
            etl_type,
            component,
            componentname,
            modulename,
            classname,
            config,
            icon,
            slug)
        values (
            '6d0e7625-5792-4b83-b14b-82f603913706',
            'Bulk Data Editor',
            'Edit Existing Data in Arches',
            'edit',
            'views/components/etl_modules/bulk-data-editor',
            'bulk-data-editor',
            'bulk_data_editor.py',
            'BulkDataEditor',
            '{"bgColor": "#7EC8E3", "circleColor": "#AEC6CF", "show": true}',
            'fa fa-edit',
            'bulk-data-editor');
        """
    remove_bulk_data_editor = """
        delete from etl_modules where etlmoduleid = '6d0e7625-5792-4b83-b14b-82f603913706';
    """

    add_stage_data_for_bulk_edit_function = """
        CREATE OR REPLACE FUNCTION __arches_stage_data_for_bulk_edit(
            load_id uuid,
            graph_id uuid,
            node_id uuid,
            module_id uuid,
            resourceinstance_ids uuid[]
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
            BEGIN
                INSERT INTO load_staging (tileid, value, nodegroupid, parenttileid, resourceid, loadid, nodegroup_depth, source_description, passes_validation)
                    SELECT DISTINCT t.tileid, t.tiledata, t.nodegroupid, t.parenttileid, t.resourceinstanceid, load_id, 0, 'bulk_edit_test', true
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
                        END;
            END;
        $$;
    """
    remove_stage_data_for_bulk_edit_function = """
        DROP FUNCTION IF EXISTS __arches_stage_data_for_bulk_edit(uuid,uuid,uuid,uuid,uuid[]);
    """

    add_edit_staged_data_function = """
        CREATE OR REPLACE FUNCTION __arches_edit_staged_data(
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
                                            WHEN 'upper' THEN
                                                FORMAT('"%s"', UPPER(updated_value -> language_code ->> 'value'))::jsonb
                                            WHEN 'lower' THEN
                                                FORMAT('"%s"', LOWER(updated_value -> language_code ->> 'value'))::jsonb
                                            WHEN 'trim' THEN
                                                FORMAT('"%s"', TRIM(updated_value -> language_code ->> 'value'))::jsonb
                                            WHEN 'capitalize' THEN
                                                FORMAT('"%s"', INITCAP(updated_value -> language_code ->> 'value'))::jsonb
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
                                'source', 'bulk-edit',
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
    remove_edit_staged_data_function = """
        DROP FUNCTION IF EXISTS __arches_edit_staged_data(uuid,uuid,uuid,text,text,text,text);
    """

    add_save_tile_for_edit_function = """
        CREATE OR REPLACE FUNCTION __arches_save_tile_for_edit(
            load_id uuid
        )
        RETURNS VOID
        LANGUAGE 'plpgsql'
        AS $$
            BEGIN
                -- create edit log records
                INSERT INTO edit_log (resourceclassid, resourceinstanceid, nodegroupid, tileinstanceid, edittype, newvalue, oldvalue, timestamp, note, transactionid)
                SELECT DISTINCT n.graphid, t.resourceinstanceid, t.nodegroupid, t.tileid, 'tile edit', t.tiledata, l.value, now(), 'bulk_edit', load_id
                FROM tiles t, nodes n, load_staging l
                WHERE t.nodegroupid = n.nodegroupid
                AND t.tileid = l.tileid
                AND l.loadid = load_id
                AND t.tiledata <> l.value;

                -- update the tiles
                UPDATE tiles
                SET tiledata = l.value
                FROM load_staging l
                WHERE tiles.tileid = l.tileid
                AND l.loadid = load_id;
            END;    
        $$;
    """
    remove_save_tile_for_edit_function = """
        DROP FUNCTION IF EXISTS __arches_save_tile_for_edit(uuid);
    """

    operations = [
        migrations.RunSQL(
            add_bulk_data_editor,
            remove_bulk_data_editor,
        ),
        migrations.RunSQL(
            add_stage_data_for_bulk_edit_function,
            remove_stage_data_for_bulk_edit_function,
        ),
        migrations.RunSQL(add_edit_staged_data_function, remove_edit_staged_data_function),
        migrations.RunSQL(add_save_tile_for_edit_function, remove_save_tile_for_edit_function),
    ]
