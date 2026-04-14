CREATE OR REPLACE FUNCTION __arches_refresh_tile_resource_relationships(tile_id uuid)
    RETURNS boolean AS
$$
DECLARE
    resourceinstancefrom_id uuid;
    from_graphid uuid;
BEGIN
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
                                                    WHERE (r.relationship->>'resourceId')::uuid = ri.resourceinstanceid) AS to_graphid
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

    RETURN true;
END;
$$ language plpgsql;
