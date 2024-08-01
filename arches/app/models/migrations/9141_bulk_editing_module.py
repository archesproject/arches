from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("models", "9075_external_oauth"),
    ]

    add_bulk_data_editor = """
        INSERT INTO etl_modules (
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
        VALUES (
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
        DELETE FROM load_staging WHERE loadid IN (SELECT loadid FROM load_event WHERE etl_module_id = '6d0e7625-5792-4b83-b14b-82f603913706');
        DELETE FROM load_event WHERE etl_module_id = '6d0e7625-5792-4b83-b14b-82f603913706';
        DELETE FROM etl_modules WHERE etlmoduleid = '6d0e7625-5792-4b83-b14b-82f603913706';
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
                    SELECT DISTINCT t.tileid, t.tiledata, t.nodegroupid, t.parenttileid, t.resourceinstanceid, load_id, 0, 'bulk_edit', true
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

    update_staging_to_tile_function = """
        CREATE OR REPLACE FUNCTION public.__arches_staging_to_tile(load_id uuid)
        RETURNS BOOLEAN AS $$
            DECLARE
                status boolean;
                staged_value jsonb;
                tile_data jsonb;
                old_data jsonb;
                passed boolean;
        		source text;
                selected_resource text;
                graph_id uuid;
                instance_id uuid;
                legacy_id text;
                file_id uuid;
                tile_id uuid;
                parent_id uuid;
                nodegroup_id uuid;
                _file jsonb;
                _key text;
                _value text;
                tile_data_value jsonb;
                resource_object jsonb;
                resource_obejct_array jsonb;
            BEGIN
                FOR staged_value, instance_id, legacy_id, tile_id, parent_id, nodegroup_id, passed, graph_id, source IN
                        (
                            SELECT value, resourceid, legacyid, tileid, parenttileid, ls.nodegroupid, passes_validation, n.graphid, source_description
                            FROM load_staging ls INNER JOIN (SELECT DISTINCT nodegroupid, graphid FROM nodes) n
                            ON ls.nodegroupid = n.nodegroupid
                            WHERE loadid = load_id
                            ORDER BY nodegroup_depth ASC
                        )
                    LOOP
                        IF passed THEN
                            SELECT resourceinstanceid FROM resource_instances INTO selected_resource WHERE resourceinstanceid = instance_id;
                            -- create a resource first if the rsource is not yet created
                            IF NOT FOUND THEN
                                INSERT INTO resource_instances(resourceinstanceid, graphid, legacyid, createdtime)
                                    VALUES (instance_id, graph_id, legacy_id, now());
                                -- create resource instance edit log
                                INSERT INTO edit_log (resourceclassid, resourceinstanceid, edittype, timestamp, note, transactionid)
                                    VALUES (graph_id, instance_id, 'create', now(), 'loaded from staging_table', load_id);
                            END IF;

                            -- create a tile one by one
                            tile_data := '{}'::jsonb;
                            FOR _key, _value IN SELECT * FROM jsonb_each_text(staged_value)
                                LOOP
                                    tile_data_value = _value::jsonb -> 'value';
                                    IF (_value::jsonb ->> 'datatype') in ('resource-instance-list', 'resource-instance') AND tile_data_value <> null THEN
                                        resource_obejct_array = '[]'::jsonb;
                                        FOR resource_object IN SELECT * FROM jsonb_array_elements(tile_data_value) LOOP
                                            resource_object = jsonb_set(resource_object, '{resourceXresourceId}', to_jsonb(uuid_generate_v1mc()));
                                            resource_obejct_array = resource_obejct_array || resource_object;
                                        END LOOP;
                                        tile_data_value = resource_obejct_array;
                                    END IF;
                                    tile_data = jsonb_set(tile_data, format('{"%s"}', _key)::text[], coalesce(tile_data_value, 'null'));
                                END LOOP;

                            SELECT tiledata FROM tiles INTO old_data WHERE resourceinstanceid = instance_id AND tileid = tile_id;
                            IF NOT FOUND THEN
                                old_data = null;
                            END IF;

                            IF source = 'bulk_edit' THEN
                                UPDATE tiles
                                    SET tiledata = tile_data
                                    WHERE tileid = tile_id;
                                INSERT INTO edit_log (resourceclassid, resourceinstanceid, nodegroupid, tileinstanceid, edittype, newvalue, oldvalue, timestamp, note, transactionid)
                                    VALUES (graph_id, instance_id, nodegroup_id, tile_id, 'tile edit', tile_data::jsonb, old_data, now(), 'loaded from staging_table', load_id);					
                            ELSE
                                INSERT INTO tiles(tileid, tiledata, nodegroupid, parenttileid, resourceinstanceid)
                                    VALUES (tile_id, tile_data, nodegroup_id, parent_id, instance_id);
                                INSERT INTO edit_log (resourceclassid, resourceinstanceid, nodegroupid, tileinstanceid, edittype, newvalue, oldvalue, timestamp, note, transactionid)
                                    VALUES (graph_id, instance_id, nodegroup_id, tile_id, 'tile create', tile_data::jsonb, old_data, now(), 'loaded from staging_table', load_id);
                            END IF;
                        END IF;
                    END LOOP;
                FOR staged_value, tile_id IN
                        (
                            SELECT value, tileid
                            FROM load_staging
                            WHERE loadid = load_id
                        )
                    LOOP
                        FOR _key, _value IN SELECT * FROM jsonb_each_text(staged_value)
                            LOOP
                                CASE
                                    WHEN (_value::jsonb ->> 'datatype') = 'file-list' THEN
                                        FOR _file IN SELECT * FROM jsonb_array_elements(_value::jsonb -> 'value') LOOP
                                            file_id = _file ->> 'file_id';
                                            UPDATE files SET tileid = tile_id WHERE fileid = file_id::uuid;
                                        END LOOP;
                                    WHEN (_value::jsonb ->> 'datatype') in ('resource-instance-list', 'resource-instance') THEN
                                        PERFORM __arches_refresh_tile_resource_relationships(tile_id);
                                    WHEN (_value::jsonb ->> 'datatype') = 'geojson-feature-collection' THEN
                                        PERFORM refresh_tile_geojson_geometries(tile_id);
                                    ELSE
                                END CASE;
                            END LOOP;
                    END LOOP;
                UPDATE load_event SET (load_end_time, complete, successful) = (now(), true, true) WHERE loadid = load_id;
                SELECT successful INTO status FROM load_event WHERE loadid = load_id;
                RETURN status;
            END;
        $$
        LANGUAGE plpgsql
    """

    revert_staging_to_tile_function = """
        CREATE OR REPLACE FUNCTION public.__arches_staging_to_tile(load_id uuid)
        RETURNS BOOLEAN AS $$
            DECLARE
                status boolean;
                staged_value jsonb;
                tile_data jsonb;
                old_data jsonb;
                passed boolean;
                selected_resource text;
                graph_id uuid;
                instance_id uuid;
                legacy_id text;
                file_id uuid;
                tile_id uuid;
                parent_id uuid;
                nodegroup_id uuid;
                _file jsonb;
                _key text;
                _value text;
                tile_data_value jsonb;
                resource_object jsonb;
                resource_obejct_array jsonb;
            BEGIN
                FOR staged_value, instance_id, legacy_id, tile_id, parent_id, nodegroup_id, passed, graph_id IN
                        (
                            SELECT value, resourceid, legacyid, tileid, parenttileid, ls.nodegroupid, passes_validation, n.graphid
                            FROM load_staging ls INNER JOIN (SELECT DISTINCT nodegroupid, graphid FROM nodes) n
                            ON ls.nodegroupid = n.nodegroupid
                            WHERE loadid = load_id
                            ORDER BY nodegroup_depth ASC
                        )
                    LOOP
                        IF passed THEN
                            SELECT resourceinstanceid FROM resource_instances INTO selected_resource WHERE resourceinstanceid = instance_id;
                            -- create a resource first if the rsource is not yet created
                            IF NOT FOUND THEN
                                INSERT INTO resource_instances(resourceinstanceid, graphid, legacyid, createdtime)
                                    VALUES (instance_id, graph_id, legacy_id, now());
                                -- create resource instance edit log
                                INSERT INTO edit_log (resourceclassid, resourceinstanceid, edittype, timestamp, note, transactionid)
                                    VALUES (graph_id, instance_id, 'create', now(), 'loaded from staging_table', load_id);
                            END IF;

                            -- create a tile one by one
                            tile_data := '{}'::jsonb;
                            FOR _key, _value IN SELECT * FROM jsonb_each_text(staged_value)
                                LOOP
                                    tile_data_value = _value::jsonb -> 'value';
                                    IF (_value::jsonb ->> 'datatype') in ('resource-instance-list', 'resource-instance') AND tile_data_value <> null THEN
                                        resource_obejct_array = '[]'::jsonb;
                                        FOR resource_object IN SELECT * FROM jsonb_array_elements(tile_data_value) LOOP
                                            resource_object = jsonb_set(resource_object, '{resourceXresourceId}', to_jsonb(uuid_generate_v1mc()));
                                            resource_obejct_array = resource_obejct_array || resource_object;
                                        END LOOP;
                                        tile_data_value = resource_obejct_array;
                                    END IF;
                                    tile_data = jsonb_set(tile_data, format('{"%s"}', _key)::text[], coalesce(tile_data_value, 'null'));
                                END LOOP;

                            SELECT tiledata FROM tiles INTO old_data WHERE resourceinstanceid = instance_id AND tileid = tile_id;
                            IF NOT FOUND THEN
                                old_data = null;
                            END IF;

                            INSERT INTO tiles(tileid, tiledata, nodegroupid, parenttileid, resourceinstanceid)
                                VALUES (tile_id, tile_data, nodegroup_id, parent_id, instance_id);
                            INSERT INTO edit_log (resourceclassid, resourceinstanceid, nodegroupid, tileinstanceid, edittype, newvalue, oldvalue, timestamp, note, transactionid)
                                VALUES (graph_id, instance_id, nodegroup_id, tile_id, 'tile create', tile_data::jsonb, old_data, now(), 'loaded from staging_table', load_id);
                        END IF;
                    END LOOP;
                FOR staged_value, tile_id IN
                        (
                            SELECT value, tileid
                            FROM load_staging
                            WHERE loadid = load_id
                        )
                    LOOP
                        FOR _key, _value IN SELECT * FROM jsonb_each_text(staged_value)
                            LOOP
                                CASE
                                    WHEN (_value::jsonb ->> 'datatype') = 'file-list' THEN
                                        FOR _file IN SELECT * FROM jsonb_array_elements(_value::jsonb -> 'value') LOOP
                                            file_id = _file ->> 'file_id';
                                            UPDATE files SET tileid = tile_id WHERE fileid = file_id::uuid;
                                        END LOOP;
                                    WHEN (_value::jsonb ->> 'datatype') in ('resource-instance-list', 'resource-instance') THEN
                                        PERFORM __arches_refresh_tile_resource_relationships(tile_id);
                                    WHEN (_value::jsonb ->> 'datatype') = 'geojson-feature-collection' THEN
                                        PERFORM refresh_tile_geojson_geometries(tile_id);
                                    ELSE
                                END CASE;
                            END LOOP;
                    END LOOP;
                UPDATE load_event SET (load_end_time, complete, successful) = (now(), true, true) WHERE loadid = load_id;
                SELECT successful INTO status FROM load_event WHERE loadid = load_id;
                RETURN status;
            END;
        $$
        LANGUAGE plpgsql
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
            update_staging_to_tile_function,
            revert_staging_to_tile_function,
        ),
        migrations.RunSQL(
            add_edit_staged_data_function, remove_edit_staged_data_function
        ),
        migrations.RunSQL(
            add_save_tile_for_edit_function, remove_save_tile_for_edit_function
        ),
    ]
