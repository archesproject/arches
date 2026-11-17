CREATE OR REPLACE FUNCTION public.__arches_refresh_transaction_resource_relationships(
    transaction_id uuid
)
RETURNS boolean AS $$
BEGIN
    DELETE FROM resource_x_resource x
    USING edit_log el
    WHERE el.transactionid = transaction_id
      AND el.tileinstanceid IS NOT NULL
      AND x.tileid = el.tileinstanceid::uuid;

    WITH transaction_tileids AS (
        -- Dedupe on the small side: DISTINCT over the joined rows would sort on
        -- tiledata, which is ruinous once a load is millions of tiles.
        SELECT DISTINCT el.tileinstanceid::uuid AS tileid
        FROM edit_log el
        WHERE el.transactionid = transaction_id
          AND el.tileinstanceid IS NOT NULL
    ),
    transaction_tiles AS (
        SELECT t.tileid, t.resourceinstanceid, t.nodegroupid, t.tiledata
        FROM tiles t
        JOIN transaction_tileids tt ON tt.tileid = t.tileid
    ),
    relationships AS (
        SELECT t.tileid,
               t.resourceinstanceid,
               n.nodeid,
               jsonb_array_elements(t.tiledata->n.nodeid::text) AS relationship
        FROM transaction_tiles t
        JOIN nodes n ON n.nodegroupid = t.nodegroupid
        WHERE n.datatype IN ('resource-instance-list', 'resource-instance')
          AND jsonb_typeof(t.tiledata->n.nodeid::text) = 'array'
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
        modified,
        resourceinstancefrom_graphid,
        resourceinstanceto_graphid
    )
    SELECT
        CASE COALESCE(r.relationship->>'resourceXresourceId', '')
            WHEN '' THEN uuid_generate_v4()
            ELSE (r.relationship->>'resourceXresourceId')::uuid
        END,
        '',
        r.relationship->>'ontologyProperty',
        r.resourceinstanceid,
        (r.relationship->>'resourceId')::uuid,
        r.relationship->>'inverseOntologyProperty',
        r.tileid,
        r.nodeid,
        now(),
        now(),
        resourcefrom.graphid,
        resourceto.graphid
    FROM relationships r
    LEFT JOIN resource_instances resourcefrom
           ON resourcefrom.resourceinstanceid = r.resourceinstanceid
    LEFT JOIN resource_instances resourceto
           ON resourceto.resourceinstanceid = (r.relationship->>'resourceId')::uuid
    WHERE r.relationship->>'resourceId' IS NOT NULL;

    RETURN true;
END;
$$ LANGUAGE plpgsql;
