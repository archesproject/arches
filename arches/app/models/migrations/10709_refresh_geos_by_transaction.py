from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("models", "9191_string_nonlocalized"),
    ]

    forward = """
        CREATE OR REPLACE FUNCTION public.refresh_transaction_geojson_geometries(
            transaction_id uuid)
            RETURNS boolean
            LANGUAGE 'plpgsql'
            COST 100
            VOLATILE PARALLEL UNSAFE
        AS $BODY$
            BEGIN
                DELETE FROM geojson_geometries USING edit_log WHERE tileinstanceid::uuid = tileid and transactionid = transaction_id;

                INSERT INTO geojson_geometries(
                    tileid,
                    resourceinstanceid,
                    nodeid,
                    geom
                )
                SELECT t.tileid,
                    t.resourceinstanceid,
                    n.nodeid,
                    ST_Force2D(
                        ST_Transform(
                            ST_SetSRID(
                                (ST_Dump(
                                    st_geomfromgeojson(
                                        (
                                            json_array_elements(
                                                t.tiledata::json->n.nodeid::text->'features'
                                            )->'geometry'
                                        )::text
                                    )
                                )).geom,
                                4326
                            ),
                            3857
                        )
                    ) AS geom
                FROM tiles t
                    LEFT JOIN nodes n ON t.nodegroupid = n.nodegroupid
                    JOIN edit_log el ON t.tileid = el.tileinstanceid::uuid  
                GROUP BY t.tileid, t.resourceinstanceid, n.nodeid, el.transactionid
                HAVING n.datatype = 'geojson-feature-collection'::text
                    AND el.transactionid = transaction_id;
                    
                RETURN TRUE;
            END;
                    
        $BODY$;

        ALTER FUNCTION public.refresh_transaction_geojson_geometries(uuid)
            OWNER TO postgres;


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
                _file jsonb;
                _key text;
                _value text;
                tile_data_value jsonb;
                resource_object jsonb;
                resource_obejct_array jsonb;
            BEGIN
                FOR staged_value, instance_id, legacy_id, tile_id, parent_id, nodegroup_id, passed, graph_id, source, op IN
                    (
                        SELECT value, resourceid, legacyid, tileid, parenttileid, ls.nodegroupid, passes_validation, n.graphid, source_description, operation
                        FROM load_staging ls INNER JOIN (SELECT DISTINCT nodegroupid, graphid FROM nodes) n
                        ON ls.nodegroupid = n.nodegroupid
                        WHERE loadid = load_id
                        ORDER BY nodegroup_depth ASC
                    )
                LOOP
                    IF passed THEN
                        SELECT resourceinstanceid FROM resource_instances INTO selected_resource WHERE resourceinstanceid = instance_id;
                        -- create a resource first if the resource is not yet created
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

        ALTER FUNCTION public.__arches_staging_to_tile(uuid)
            OWNER TO postgres;
        """

    reverse = """
        DROP FUNCTION IF EXISTS public.refresh_transaction_geojson_geometries(uuid);

        CREATE OR REPLACE FUNCTION public.__arches_staging_to_tile(load_id uuid)
        RETURNS BOOLEAN AS $$
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
                _file jsonb;
                _key text;
                _value text;
                tile_data_value jsonb;
                resource_object jsonb;
                resource_obejct_array jsonb;
            BEGIN
                FOR staged_value, instance_id, legacy_id, tile_id, parent_id, nodegroup_id, passed, graph_id, source, op IN
                    (
                        SELECT value, resourceid, legacyid, tileid, parenttileid, ls.nodegroupid, passes_validation, n.graphid, source_description, operation
                        FROM load_staging ls INNER JOIN (SELECT DISTINCT nodegroupid, graphid FROM nodes) n
                        ON ls.nodegroupid = n.nodegroupid
                        WHERE loadid = load_id
                        ORDER BY nodegroup_depth ASC
                    )
                LOOP
                    IF passed THEN
                        SELECT resourceinstanceid FROM resource_instances INTO selected_resource WHERE resourceinstanceid = instance_id;
                        -- create a resource first if the resource is not yet created
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
            forward,
            reverse,
        ),
    ]