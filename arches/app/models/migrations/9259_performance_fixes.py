from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("models", "9165_error_reporting"),
    ]

    forward_sql = """
    CREATE OR REPLACE FUNCTION public.__arches_create_resource_x_resource_relationships(
	tile_id uuid)
    RETURNS boolean
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    AS $BODY$
            DECLARE
                resourceinstancefrom_id uuid;
                from_graphid uuid;
                relational_count text;
                val boolean = true;
            BEGIN
                select count(*) into relational_count from tiles where tiledata::text like '%resourceX%' and tileid = tile_id;

                IF relational_count = '0' 
                    THEN 
                    RETURN false;
                END IF; 
                    
                --https://dbfiddle.uk/?rdbms=postgres_12&fiddle=21e25754f355a492dfd7b4a134182d2e

                SELECT resourceinstanceid INTO resourceinstancefrom_id FROM tiles WHERE tileid = tile_id; 
                SELECT graphid INTO from_graphid FROM resource_instances WHERE resourceinstanceid = resourceinstancefrom_id; 

                DELETE FROM resource_x_resource WHERE tileid = tile_id;

                WITH updated_tiles as (
                    select * from tiles t
                    WHERE
                        t.tileid = tile_id
                )
                , relationships AS (
                    SELECT n.nodeid, n.config,
                        jsonb_array_elements(tt.tiledata->n.nodeid::text) AS relationship
                    FROM updated_tiles tt
                        LEFT JOIN nodes n ON tt.nodegroupid = n.nodegroupid
                    WHERE n.datatype IN ('resource-instance-list', 'resource-instance')
                        AND tt.tiledata->>n.nodeid::text IS NOT null
                )
                , relationships2 AS (
                    SELECT r.nodeid, r.config, r.relationship, (SELECT ri.graphid
                        FROM resource_instances ri
                        WHERE r.relationship->>'resourceId' = ri.resourceinstanceid::text) AS to_graphid
                    FROM relationships r
                )
                , relationships3 AS (
                    SELECT fr.nodeid, fr.relationship, fr.to_graphid, 
                    (
                        SELECT graphs->>'ontologyProperty'
                        FROM jsonb_array_elements(fr.config->'graphs') AS graphs
                        WHERE graphs->>'graphid' = fr.to_graphid::text
                    ) AS defaultOntologyProperty,
                    (
                        SELECT graphs->>'inverseOntologyProperty'
                        FROM jsonb_array_elements(fr.config->'graphs') AS graphs
                        WHERE graphs->>'graphid' = fr.to_graphid::text
                    ) AS defaultInverseOntologyProperty
                    FROM relationships2 fr
                )

                INSERT INTO resource_x_resource (
                    resourcexid,
                    notes,
                    relationshiptype,
                    inverserelationshiptype,
                    resourceinstanceidfrom,
                    resourceinstanceidto,
                    resourceinstancefrom_graphid,
                    resourceinstanceto_graphid,
                    tileid,
                    nodeid,
                    created,
                    modified
                ) (SELECT
                    CASE relationship->>'resourceXresourceId'
                        WHEN '' THEN uuid_generate_v4()
                        ELSE (relationship->>'resourceXresourceId')::uuid
                    END,
                    '',
                    CASE relationship->>'ontologyProperty'
                        WHEN '' THEN defaultOntologyProperty
                        ELSE relationship->>'ontologyProperty'
                    END,
                    CASE relationship->>'inverseOntologyProperty'
                        WHEN '' THEN defaultInverseOntologyProperty
                        ELSE relationship->>'inverseOntologyProperty'
                    END,
                    resourceinstancefrom_id,
                    (relationship->>'resourceId')::uuid,
                    from_graphid,
                    to_graphid,
                    tile_id,
                    nodeid,
                    now(),
                    now()
                FROM relationships3);
                RETURN val;
            END;
            $BODY$;
    """

    reverse_sql = """
        CREATE OR REPLACE FUNCTION public.__arches_create_resource_x_resource_relationships(IN tile_id uuid)
            RETURNS boolean
            LANGUAGE 'plpgsql'
            VOLATILE
            PARALLEL UNSAFE
            COST 100
            
        AS $BODY$
        DECLARE
            resourceinstancefrom_id uuid;
            from_graphid uuid;
            val boolean = true;
        BEGIN
            --https://dbfiddle.uk/?rdbms=postgres_12&fiddle=21e25754f355a492dfd7b4a134182d2e

            SELECT resourceinstanceid INTO resourceinstancefrom_id FROM tiles WHERE tileid = tile_id; 
            SELECT graphid INTO from_graphid FROM resource_instances WHERE resourceinstanceid = resourceinstancefrom_id; 

            DELETE FROM resource_x_resource WHERE tileid = tile_id;

            WITH updated_tiles as (
                UPDATE tiles t
                SET tiledata = ret.result
                FROM (SELECT res.tileid, (res.tiledata || jsonb_object_agg(res.nodeid, res.result)) result
                        FROM 
                        nodes n, 
                            (SELECT t.tileid, n.nodeid, t.tiledata, jsonb_agg(jsonb_set(tile_data, array['resourceXresourceId'::text], ('"' || uuid_generate_v4()|| '"')::jsonb, true)) result
                                FROM tiles t LEFT JOIN nodes n ON t.nodegroupid = n.nodegroupid, jsonb_array_elements(t.tiledata->n.nodeid::text) tile_data
                                WHERE t.tiledata->>n.nodeid::text IS NOT null
                                AND t.tiledata->>n.nodeid::text != ''
                                AND t.tileid = tile_id
                                AND n.datatype IN ('resource-instance-list', 'resource-instance')
                                GROUP BY t.tileid, n.nodeid, tiledata
                            ) res
                        WHERE n.nodeid = res.nodeid
                        GROUP BY res.tileid, res.tiledata
                    ) as ret
                WHERE
                    t.tileid = tile_id
                RETURNING t.nodegroupid, t.tiledata::jsonb, t.tileid, t.resourceinstanceid
            )
            , relationships AS (
                SELECT n.nodeid, n.config,
                    jsonb_array_elements(tt.tiledata->n.nodeid::text) AS relationship
                FROM updated_tiles tt
                    LEFT JOIN nodes n ON tt.nodegroupid = n.nodegroupid
                WHERE n.datatype IN ('resource-instance-list', 'resource-instance')
                    AND tt.tiledata->>n.nodeid::text IS NOT null
            )
            , relationships2 AS (
                SELECT r.nodeid, r.config, r.relationship, (SELECT ri.graphid
                    FROM resource_instances ri
                    WHERE r.relationship->>'resourceId' = ri.resourceinstanceid::text) AS to_graphid
                FROM relationships r
            )
            , relationships3 AS (
                SELECT fr.nodeid, fr.relationship, fr.to_graphid, 
                (
                    SELECT graphs->>'ontologyProperty'
                    FROM jsonb_array_elements(fr.config->'graphs') AS graphs
                    WHERE graphs->>'graphid' = fr.to_graphid::text
                ) AS defaultOntologyProperty,
                (
                    SELECT graphs->>'inverseOntologyProperty'
                    FROM jsonb_array_elements(fr.config->'graphs') AS graphs
                    WHERE graphs->>'graphid' = fr.to_graphid::text
                ) AS defaultInverseOntologyProperty
                FROM relationships2 fr
            )

            INSERT INTO resource_x_resource (
                resourcexid,
                notes,
                relationshiptype,
                inverserelationshiptype,
                resourceinstanceidfrom,
                resourceinstanceidto,
                resourceinstancefrom_graphid,
                resourceinstanceto_graphid,
                tileid,
                nodeid,
                created,
                modified
            ) (SELECT
                (relationship->>'resourceXresourceId')::uuid,
                '',
                CASE relationship->>'ontologyProperty'
                    WHEN '' THEN defaultOntologyProperty
                    ELSE relationship->>'ontologyProperty'
                END,
                CASE relationship->>'inverseOntologyProperty'
                    WHEN '' THEN defaultInverseOntologyProperty
                    ELSE relationship->>'inverseOntologyProperty'
                END,
                resourceinstancefrom_id,
                (relationship->>'resourceId')::uuid,
                from_graphid,
                to_graphid,
                tile_id,
                nodeid,
                now(),
                now()
            FROM relationships3);

            RETURN val;
        END;
        $BODY$;

    """

    operations = [
        migrations.RunSQL(forward_sql, reverse_sql),
    ]
