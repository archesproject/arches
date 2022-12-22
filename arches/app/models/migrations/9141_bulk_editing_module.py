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
                tile_id uuid;
                tile_data jsonb;
                nodegroup_id uuid;
                parenttile_id uuid;
                resourceinstance_id uuid;
                data_type text;
                transform_sql text;
                data_for_staging jsonb;

            BEGIN
                SELECT datatype INTO data_type FROM nodes WHERE nodeid = node_id;
                data_for_staging := '{}'::jsonb;
                UPDATE load_staging
                SET value = jsonb_set(
                    value,
                    FORMAT('{%I, "en", "value"}', node_id)::text[],
                    CASE operation
                        WHEN 'replace' THEN
                            FORMAT('"%s"', REPLACE(value -> node_id::text -> 'en' ->> 'value', old_text, new_text))::jsonb
                        WHEN 'upper' THEN
                            FORMAT('"%s"', UPPER(value -> node_id::text -> 'en' ->> 'value'))::jsonb
                        WHEN 'lower' THEN
                            FORMAT('"%s"', LOWER(value -> node_id::text -> 'en' ->> 'value'))::jsonb
                        WHEN 'trim' THEN
                            FORMAT('"%s"', TRIM(value -> node_id::text -> 'en' ->> 'value'))::jsonb
                        WHEN 'capitalize' THEN
                            FORMAT('"%s"', INITCAP(value -> node_id::text -> 'en' ->> 'value'))::jsonb
                    END
                )
                WHERE loadid = load_id;
            END;
        $$;
    """
    remove_edit_staged_data_function = """
        DROP FUNCTION IF EXISTS __arches_edit_staged_data(uuid,uuid,text,text,text,text);
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
        migrations.RunSQL(
            add_edit_staged_data_function,
            remove_edit_staged_data_function
        ),
        migrations.RunSQL(
            add_save_tile_for_edit_function,
            remove_save_tile_for_edit_function
        ),
    ]
