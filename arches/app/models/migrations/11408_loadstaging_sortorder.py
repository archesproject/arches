from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "10437_node_alias_not_null"),
    ]

    update_arches_staging_to_tile = """
        CREATE OR REPLACE FUNCTION public.__arches_staging_to_tile(
            load_id uuid)
            RETURNS boolean
            LANGUAGE 'plpgsql'
            COST 100
            VOLATILE PARALLEL UNSAFE
        AS $BODY$
            DECLARE
                status boolean;
                staged_value jsonb;
                tile_data jsonb;
                old_data jsonb;
                passed boolean;
                source text;
                op text;
                selected_resource text;
                graph_id uuid;
                instance_id uuid;
                legacy_id text;
                file_id uuid;
                tile_id uuid;
                tile_id_tree uuid;
                parent_id uuid;
                nodegroup_id uuid;
                sort_order integer;
                resource_instance_lifecycle_state_uuid uuid;
                _file jsonb;
                _key text;
                _value text;
                tile_data_value jsonb;
                resource_object jsonb;
                resource_obejct_array jsonb;
            BEGIN
                FOR staged_value, instance_id, legacy_id, tile_id, parent_id, nodegroup_id, passed, graph_id, source, op, resource_instance_lifecycle_state_uuid, sort_order IN
                    (
                        SELECT value, resourceid, legacyid, tileid, parenttileid, ls.nodegroupid, passes_validation, n.graphid, source_description, operation, rils.id, ls.sortorder
                        FROM load_staging ls 
                        INNER JOIN (SELECT DISTINCT nodegroupid, graphid FROM nodes) n
                        ON ls.nodegroupid = n.nodegroupid
                        INNER JOIN (SELECT graphid, resource_instance_lifecycle_id FROM graphs) g
                        ON g.graphid = n.graphid
                        INNER JOIN (SELECT id, resource_instance_lifecycle_id FROM resource_instance_lifecycle_states WHERE is_initial_state = true) rils
                        ON g.resource_instance_lifecycle_id = rils.resource_instance_lifecycle_id
                        WHERE loadid = load_id
                        ORDER BY nodegroup_depth ASC
                    )
                LOOP
                    IF passed THEN
                        SELECT resourceinstanceid FROM resource_instances INTO selected_resource WHERE resourceinstanceid = instance_id;
                        -- create a resource first if the resource is not yet created
                        IF NOT FOUND THEN
                            INSERT INTO resource_instances(resourceinstanceid, graphid, legacyid, createdtime, resource_instance_lifecycle_state_id)
                                VALUES (instance_id, graph_id, legacy_id, now(), resource_instance_lifecycle_state_uuid);
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

                        IF op = 'update' THEN
                            SELECT tiledata FROM tiles INTO old_data WHERE resourceinstanceid = instance_id AND tileid = tile_id;
                            IF NOT FOUND THEN
                                INSERT INTO tiles(tileid, tiledata, nodegroupid, parenttileid, resourceinstanceid, sortorder)
                                    VALUES (tile_id, tile_data, nodegroup_id, parent_id, instance_id, sort_order);
                                INSERT INTO edit_log (resourceclassid, resourceinstanceid, nodegroupid, tileinstanceid, edittype, newvalue, timestamp, note, transactionid)
                                    VALUES (graph_id, instance_id, nodegroup_id, tile_id, 'tile create', tile_data::jsonb, now(), 'loaded from staging_table', load_id);
                            ELSE
                                UPDATE tiles
                                    SET tiledata = tile_data, sortorder = sort_order
                                    WHERE tileid = tile_id;
                                INSERT INTO edit_log (resourceclassid, resourceinstanceid, nodegroupid, tileinstanceid, edittype, newvalue, oldvalue, timestamp, note, transactionid)
                                    VALUES (graph_id, instance_id, nodegroup_id, tile_id, 'tile edit', tile_data::jsonb, old_data, now(), 'loaded from staging_table', load_id);
                            END IF;
                        ELSIF op = 'insert' THEN
                            INSERT INTO tiles(tileid, tiledata, nodegroupid, parenttileid, resourceinstanceid, sortorder)
                                VALUES (tile_id, tile_data, nodegroup_id, parent_id, instance_id, sort_order);
                            INSERT INTO edit_log (resourceclassid, resourceinstanceid, nodegroupid, tileinstanceid, edittype, newvalue, timestamp, note, transactionid)
                                VALUES (graph_id, instance_id, nodegroup_id, tile_id, 'tile create', tile_data::jsonb, now(), 'loaded from staging_table', load_id);
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
                                ELSE
                            END CASE;
                        END LOOP;
                END LOOP;
                UPDATE load_event SET (load_end_time, complete, successful) = (now(), true, true) WHERE loadid = load_id;
                PERFORM refresh_transaction_geojson_geometries(load_id);
                SELECT successful INTO status FROM load_event WHERE loadid = load_id;
                RETURN status;
            END;
        $BODY$;
    """

    reverse_arches_staging_to_tile = """
        CREATE OR REPLACE FUNCTION public.__arches_staging_to_tile(
            load_id uuid)
            RETURNS boolean
            LANGUAGE 'plpgsql'
            COST 100
            VOLATILE PARALLEL UNSAFE
        AS $BODY$
            DECLARE
                status boolean;
                staged_value jsonb;
                tile_data jsonb;
                old_data jsonb;
                passed boolean;
                source text;
                op text;
                selected_resource text;
                graph_id uuid;
                instance_id uuid;
                legacy_id text;
                file_id uuid;
                tile_id uuid;
                tile_id_tree uuid;
                parent_id uuid;
                nodegroup_id uuid;
                resource_instance_lifecycle_state_uuid uuid;
                _file jsonb;
                _key text;
                _value text;
                tile_data_value jsonb;
                resource_object jsonb;
                resource_obejct_array jsonb;
            BEGIN
                FOR staged_value, instance_id, legacy_id, tile_id, parent_id, nodegroup_id, passed, graph_id, source, op, resource_instance_lifecycle_state_uuid IN
                    (
                        SELECT value, resourceid, legacyid, tileid, parenttileid, ls.nodegroupid, passes_validation, n.graphid, source_description, operation, rils.id
                        FROM load_staging ls 
                        INNER JOIN (SELECT DISTINCT nodegroupid, graphid FROM nodes) n
                        ON ls.nodegroupid = n.nodegroupid
                        INNER JOIN (SELECT graphid, resource_instance_lifecycle_id FROM graphs) g
                        ON g.graphid = n.graphid
                        INNER JOIN (SELECT id, resource_instance_lifecycle_id FROM resource_instance_lifecycle_states WHERE is_initial_state = true) rils
                        ON g.resource_instance_lifecycle_id = rils.resource_instance_lifecycle_id
                        WHERE loadid = load_id
                        ORDER BY nodegroup_depth ASC
                    )
                LOOP
                    IF passed THEN
                        SELECT resourceinstanceid FROM resource_instances INTO selected_resource WHERE resourceinstanceid = instance_id;
                        -- create a resource first if the resource is not yet created
                        IF NOT FOUND THEN
                            INSERT INTO resource_instances(resourceinstanceid, graphid, legacyid, createdtime, resource_instance_lifecycle_state_id)
                                VALUES (instance_id, graph_id, legacy_id, now(), resource_instance_lifecycle_state_uuid);
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

                        IF op = 'update' THEN
                            SELECT tiledata FROM tiles INTO old_data WHERE resourceinstanceid = instance_id AND tileid = tile_id;
                            IF NOT FOUND THEN
                                INSERT INTO tiles(tileid, tiledata, nodegroupid, parenttileid, resourceinstanceid)
                                    VALUES (tile_id, tile_data, nodegroup_id, parent_id, instance_id);
                                INSERT INTO edit_log (resourceclassid, resourceinstanceid, nodegroupid, tileinstanceid, edittype, newvalue, timestamp, note, transactionid)
                                    VALUES (graph_id, instance_id, nodegroup_id, tile_id, 'tile create', tile_data::jsonb, now(), 'loaded from staging_table', load_id);
                            ELSE
                                UPDATE tiles
                                    SET tiledata = tile_data
                                    WHERE tileid = tile_id;
                                INSERT INTO edit_log (resourceclassid, resourceinstanceid, nodegroupid, tileinstanceid, edittype, newvalue, oldvalue, timestamp, note, transactionid)
                                    VALUES (graph_id, instance_id, nodegroup_id, tile_id, 'tile edit', tile_data::jsonb, old_data, now(), 'loaded from staging_table', load_id);
                            END IF;
                        ELSIF op = 'insert' THEN
                            INSERT INTO tiles(tileid, tiledata, nodegroupid, parenttileid, resourceinstanceid)
                                VALUES (tile_id, tile_data, nodegroup_id, parent_id, instance_id);
                            INSERT INTO edit_log (resourceclassid, resourceinstanceid, nodegroupid, tileinstanceid, edittype, newvalue, timestamp, note, transactionid)
                                VALUES (graph_id, instance_id, nodegroup_id, tile_id, 'tile create', tile_data::jsonb, now(), 'loaded from staging_table', load_id);
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
                                ELSE
                            END CASE;
                        END LOOP;
                END LOOP;
                UPDATE load_event SET (load_end_time, complete, successful) = (now(), true, true) WHERE loadid = load_id;
                PERFORM refresh_transaction_geojson_geometries(load_id);
                SELECT successful INTO status FROM load_event WHERE loadid = load_id;
                RETURN status;
            END;
        $BODY$;
    """

    update_arches_stage_string_data_for_bulk_edit = """
        CREATE OR REPLACE FUNCTION public.__arches_stage_string_data_for_bulk_edit(
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
            update_limit integer)
            RETURNS void
            LANGUAGE 'plpgsql'
            COST 100
            VOLATILE PARALLEL UNSAFE
        AS $BODY$
            DECLARE
                tile_id uuid;
                tile_data jsonb;
                nodegroup_id uuid;
                parenttile_id uuid;
                resourceinstance_id uuid;
                text_replacing_like text;
            BEGIN
                INSERT INTO load_staging (tileid, value, nodegroupid, parenttileid, resourceid, loadid, nodegroup_depth, source_description, operation, passes_validation, sortorder)
                    SELECT DISTINCT t.tileid, t.tiledata, t.nodegroupid, t.parenttileid, t.resourceinstanceid, load_id, 0, 'bulk_edit', 'update', true, t.sortorder
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
        $BODY$;
    """

    reverse_arches_stage_string_data_for_bulk_edit = """
        CREATE OR REPLACE FUNCTION public.__arches_stage_string_data_for_bulk_edit(
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
            update_limit integer)
            RETURNS void
            LANGUAGE 'plpgsql'
            COST 100
            VOLATILE PARALLEL UNSAFE
        AS $BODY$
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
        $BODY$;
    """

    operations = [
        migrations.AddField(
            model_name="loadstaging",
            name="sortorder",
            field=models.IntegerField(default=0),
        ),
        migrations.RunSQL(
            update_arches_staging_to_tile,
            reverse_arches_staging_to_tile,
        ),
        migrations.RunSQL(
            update_arches_stage_string_data_for_bulk_edit,
            reverse_arches_stage_string_data_for_bulk_edit,
        ),
    ]
