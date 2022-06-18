from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ("models", "8528_bulk_load_performance_functions"),
    ]

    forward_sql = """
        CREATE OR REPLACE FUNCTION public.__arches_create_resource_x_resource_relationships(IN tile_id uuid)
            RETURNS boolean
            LANGUAGE 'plpgsql'
            VOLATILE
            PARALLEL UNSAFE
            COST 100
            
        AS $BODY$
        DECLARE
            resource_id uuid;
            val boolean = true;
        BEGIN
            --https://dbfiddle.uk/?rdbms=postgres_12&fiddle=21e25754f355a492dfd7b4a134182d2e

            SELECT resourceinstanceid INTO resource_id FROM tiles WHERE tileid = tile_id;

            DELETE FROM resource_x_resource WHERE tileid = tile_id;

            WITH updated_tiles as (
                UPDATE tiles t
                SET tiledata = ret.result
                FROM nodes n, 
                    (SELECT res.tileid, (res.tiledata || jsonb_object_agg(res.nodeid, res.result)) result
                        FROM 
                        nodes n, 
                            (SELECT t.tileid, n.nodeid, t.tiledata, jsonb_agg(jsonb_set(tile_data, array['resourceXresourceId'::text], ('"' || uuid_generate_v4()|| '"')::jsonb, false)) result
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
                RETURNING t.nodegroupid, t.tiledata::jsonb, t.tileid
            )
            , relationships AS (
                SELECT n.nodeid,
                    jsonb_array_elements(tt.tiledata->n.nodeid::text) AS relationship
                FROM updated_tiles tt
                    LEFT JOIN nodes n ON tt.nodegroupid = n.nodegroupid
                WHERE n.datatype IN ('resource-instance-list', 'resource-instance')
                    AND tt.tiledata->>n.nodeid::text IS NOT null
            )

            INSERT INTO resource_x_resource (
                resourcexid,
                notes,
                relationshiptype,
                resourceinstanceidfrom,
                resourceinstanceidto,
                inverserelationshiptype,
                tileid,
                nodeid,
                created,
                modified
            ) (SELECT
                (relationship->>'resourceXresourceId')::uuid,
                '',
                relationship->>'ontologyProperty',
                resource_id,
                (relationship->>'resourceId')::uuid,
                relationship->>'inverseOntologyProperty',
                tile_id,
                nodeid,
                now(),
                now()
            FROM relationships);

            RETURN val;
        END;
        $BODY$;

    """

    reverse_sql = "DROP FUNCTION IF EXISTS __arches_create_resource_x_resource_relationships(uuid);"

    operations = [
        migrations.RunSQL(forward_sql, reverse_sql),
    ]
