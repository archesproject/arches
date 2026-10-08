from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("models", "12913_remove_geocoders"),
    ]

    # Collapse the four relationship keys on each entry of a resource-instance node's
    # config.graphs into a single discriminator plus one pair of values, so that a
    # relationship type can also be drawn from a controlled list:
    #   useOntologyRelationship  -> relationshipSource ('ontology'|'concept'|'reference')
    #     (when not using the ontology, the relationship is a 'concept' if its value is a
    #     UUID (RDM value id), and a 'reference' if it is anything else, i.e. a URI from a
    #     controlled list)
    #   ontologyProperty         -> relationship
    #   inverseOntologyProperty  -> inverseRelationship
    #   relationshipConcept      -> relationship
    #   inverseRelationshipConcept -> inverseRelationship
    update_node_configs = """
        UPDATE nodes SET config = jsonb_set(config, '{graphs}', (
            SELECT jsonb_agg(
                (element
                    - 'useOntologyRelationship'
                    - 'ontologyProperty'
                    - 'inverseOntologyProperty'
                    - 'relationshipConcept'
                    - 'inverseRelationshipConcept'
                ) || jsonb_build_object(
                    'relationshipSource',
                    CASE
                        WHEN element->>'useOntologyRelationship' = 'true' THEN 'ontology'
                        WHEN COALESCE(
                            NULLIF(element->>'relationshipConcept', ''),
                            NULLIF(element->>'inverseRelationshipConcept', '')
                        ) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
                        OR COALESCE(
                            NULLIF(element->>'relationshipConcept', ''),
                            NULLIF(element->>'inverseRelationshipConcept', '')
                        ) IS NULL THEN 'concept'
                        ELSE 'reference'
                    END,
                    'relationship',
                    CASE WHEN element->>'useOntologyRelationship' = 'true'
                        THEN element->'ontologyProperty' ELSE element->'relationshipConcept' END,
                    'inverseRelationship',
                    CASE WHEN element->>'useOntologyRelationship' = 'true'
                        THEN element->'inverseOntologyProperty' ELSE element->'inverseRelationshipConcept' END
                )
            )
            FROM jsonb_array_elements(config -> 'graphs') element
        ))
        WHERE datatype IN ('resource-instance', 'resource-instance-list')
        AND jsonb_typeof(config -> 'graphs') = 'array'
        AND jsonb_array_length(config -> 'graphs') > 0
        AND EXISTS (
            SELECT * FROM jsonb_array_elements(config -> 'graphs')
            WHERE value->'relationshipSource' IS NULL
        );
    """

    # Lossy: the unused side of each pair was discarded going forward. 'concept' and
    # 'reference' both restore to useOntologyRelationship false, with the relationship
    # (a UUID or a URI respectively) kept in relationshipConcept.
    reverse_node_configs = """
        UPDATE nodes SET config = jsonb_set(config, '{graphs}', (
            SELECT jsonb_agg(
                (element
                    - 'relationshipSource'
                    - 'relationship'
                    - 'inverseRelationship'
                ) || jsonb_build_object(
                    'useOntologyRelationship',
                    element->>'relationshipSource' = 'ontology',
                    'ontologyProperty',
                    CASE WHEN element->>'relationshipSource' = 'ontology'
                        THEN element->'relationship' ELSE 'null'::jsonb END,
                    'inverseOntologyProperty',
                    CASE WHEN element->>'relationshipSource' = 'ontology'
                        THEN element->'inverseRelationship' ELSE 'null'::jsonb END,
                    'relationshipConcept',
                    CASE WHEN element->>'relationshipSource' = 'ontology'
                        THEN 'null'::jsonb ELSE element->'relationship' END,
                    'inverseRelationshipConcept',
                    CASE WHEN element->>'relationshipSource' = 'ontology'
                        THEN 'null'::jsonb ELSE element->'inverseRelationship' END
                )
            )
            FROM jsonb_array_elements(config -> 'graphs') element
        ))
        WHERE datatype IN ('resource-instance', 'resource-instance-list')
        AND jsonb_typeof(config -> 'graphs') = 'array'
        AND jsonb_array_length(config -> 'graphs') > 0
        AND EXISTS (
            SELECT * FROM jsonb_array_elements(config -> 'graphs')
            WHERE value->'relationshipSource' IS NOT NULL
        );
    """

    update_relationship_function = """
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
                    WHERE (r.relationship->>'resourceId')::uuid = ri.resourceinstanceid) AS to_graphid
                FROM relationships r
            )
            , relationships3 AS (
                SELECT fr.nodeid, fr.relationship, fr.to_graphid,
                (
                    SELECT COALESCE(graphs->>'relationship', graphs->>'ontologyProperty')
                    FROM jsonb_array_elements(fr.config->'graphs') AS graphs
                    WHERE graphs->>'graphid' = fr.to_graphid::text
                ) AS defaultOntologyProperty,
                (
                    SELECT COALESCE(graphs->>'inverseRelationship', graphs->>'inverseOntologyProperty')
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
                CASE COALESCE(relationship->>'relationship', relationship->>'ontologyProperty')
                    WHEN '' THEN defaultOntologyProperty
                    ELSE COALESCE(relationship->>'relationship', relationship->>'ontologyProperty')
                END,
                CASE COALESCE(relationship->>'inverseRelationship', relationship->>'inverseOntologyProperty')
                    WHEN '' THEN defaultInverseOntologyProperty
                    ELSE COALESCE(relationship->>'inverseRelationship', relationship->>'inverseOntologyProperty')
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

    reverse_relationship_function = """
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
            RETURN val;
        END;
        $BODY$;
    """

    update_tile_data = """
        DO $$
        DECLARE
            node RECORD;
        BEGIN
            FOR node IN
                SELECT nodeid, nodegroupid FROM nodes
                WHERE datatype IN ('resource-instance', 'resource-instance-list')
            LOOP
                UPDATE tiles SET tiledata = jsonb_set(tiledata, ARRAY[node.nodeid::text], (
                    SELECT jsonb_agg(
                        CASE WHEN jsonb_typeof(element) = 'object' THEN
                            (element - 'ontologyProperty' - 'inverseOntologyProperty')
                            || CASE WHEN element->'ontologyProperty' IS NOT NULL
                                THEN jsonb_build_object('relationship', element->'ontologyProperty')
                                ELSE '{}'::jsonb END
                            || CASE WHEN element->'inverseOntologyProperty' IS NOT NULL
                                THEN jsonb_build_object('inverseRelationship', element->'inverseOntologyProperty')
                                ELSE '{}'::jsonb END
                        ELSE element END
                    )
                    FROM jsonb_array_elements(tiledata->node.nodeid::text) element
                ))
                WHERE nodegroupid = node.nodegroupid
                AND jsonb_typeof(tiledata->node.nodeid::text) = 'array'
                AND EXISTS (
                    SELECT * FROM jsonb_array_elements(tiledata->node.nodeid::text) element
                    WHERE jsonb_typeof(element) = 'object'
                    AND (element->'ontologyProperty' IS NOT NULL
                        OR element->'inverseOntologyProperty' IS NOT NULL)
                );
            END LOOP;
        END
        $$;
    """

    reverse_tile_data = """
        DO $$
        DECLARE
            node RECORD;
        BEGIN
            FOR node IN
                SELECT nodeid, nodegroupid FROM nodes
                WHERE datatype IN ('resource-instance', 'resource-instance-list')
            LOOP
                UPDATE tiles SET tiledata = jsonb_set(tiledata, ARRAY[node.nodeid::text], (
                    SELECT jsonb_agg(
                        CASE WHEN jsonb_typeof(element) = 'object' THEN
                            (element - 'relationship' - 'inverseRelationship')
                            || CASE WHEN element->'relationship' IS NOT NULL
                                THEN jsonb_build_object('ontologyProperty', element->'relationship')
                                ELSE '{}'::jsonb END
                            || CASE WHEN element->'inverseRelationship' IS NOT NULL
                                THEN jsonb_build_object('inverseOntologyProperty', element->'inverseRelationship')
                                ELSE '{}'::jsonb END
                        ELSE element END
                    )
                    FROM jsonb_array_elements(tiledata->node.nodeid::text) element
                ))
                WHERE nodegroupid = node.nodegroupid
                AND jsonb_typeof(tiledata->node.nodeid::text) = 'array'
                AND EXISTS (
                    SELECT * FROM jsonb_array_elements(tiledata->node.nodeid::text) element
                    WHERE jsonb_typeof(element) = 'object'
                    AND (element->'relationship' IS NOT NULL
                        OR element->'inverseRelationship' IS NOT NULL)
                );
            END LOOP;
        END
        $$;
    """

    update_refresh_function = """
        CREATE OR REPLACE FUNCTION public.__arches_refresh_tile_resource_relationships(tile_id uuid)
        RETURNS boolean
        LANGUAGE plpgsql
        AS $function$
        DECLARE
            resource_id uuid;
        BEGIN
            SELECT resourceinstanceid INTO resource_id FROM tiles WHERE tileid = tile_id;

            DELETE FROM resource_x_resource WHERE tileid = tile_id;

            WITH relationships AS (
                SELECT n.nodeid,
                    jsonb_array_elements(t.tiledata->n.nodeid::text) AS relationship
                FROM tiles t
                    LEFT JOIN nodes n ON t.nodegroupid = n.nodegroupid
                WHERE n.datatype IN ('resource-instance-list', 'resource-instance')
                    AND t.tileid = tile_id
                    AND t.tiledata->>n.nodeid::text IS NOT null
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
            ) SELECT
                CASE relationship->>'resourceXresourceId'
                    WHEN '' THEN uuid_generate_v4()
                    ELSE (relationship->>'resourceXresourceId')::uuid
                END,
                '',
                COALESCE(relationship->>'relationship', relationship->>'ontologyProperty'),
                resource_id,
                (relationship->>'resourceId')::uuid,
                COALESCE(relationship->>'inverseRelationship', relationship->>'inverseOntologyProperty'),
                tile_id,
                nodeid,
                now(),
                now(),
                resourcefrom.graphid,
                resourceto.graphid
            FROM relationships r
                LEFT JOIN resource_instances resourcefrom ON resourcefrom.resourceinstanceid = resource_id
                LEFT JOIN resource_instances resourceto ON resourceto.resourceinstanceid = (r.relationship ->> 'resourceId')::uuid;
            RETURN true;
        END;
        $function$
    """

    reverse_refresh_function = """
        CREATE OR REPLACE FUNCTION public.__arches_refresh_tile_resource_relationships(tile_id uuid)
        RETURNS boolean
        LANGUAGE plpgsql
        AS $function$
        DECLARE
            resource_id uuid;
        BEGIN
            SELECT resourceinstanceid INTO resource_id FROM tiles WHERE tileid = tile_id;

            DELETE FROM resource_x_resource WHERE tileid = tile_id;

            WITH relationships AS (
                SELECT n.nodeid,
                    jsonb_array_elements(t.tiledata->n.nodeid::text) AS relationship
                FROM tiles t
                    LEFT JOIN nodes n ON t.nodegroupid = n.nodegroupid
                WHERE n.datatype IN ('resource-instance-list', 'resource-instance')
                    AND t.tileid = tile_id
                    AND t.tiledata->>n.nodeid::text IS NOT null
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
            ) SELECT
                CASE relationship->>'resourceXresourceId'
                    WHEN '' THEN uuid_generate_v4()
                    ELSE (relationship->>'resourceXresourceId')::uuid
                END,
                '',
                relationship->>'ontologyProperty',
                resource_id,
                (relationship->>'resourceId')::uuid,
                relationship->>'inverseOntologyProperty',
                tile_id,
                nodeid,
                now(),
                now(),
                resourcefrom.graphid,
                resourceto.graphid
            FROM relationships r
                LEFT JOIN resource_instances resourcefrom ON resourcefrom.resourceinstanceid = resource_id
                LEFT JOIN resource_instances resourceto ON resourceto.resourceinstanceid = (r.relationship ->> 'resourceId')::uuid;
            RETURN true;
        END;
        $function$
    """

    operations = [
        migrations.RunSQL(update_node_configs, reverse_node_configs),
        migrations.RunSQL(update_tile_data, reverse_tile_data),
        migrations.RunSQL(update_relationship_function, reverse_relationship_function),
        migrations.RunSQL(update_refresh_function, reverse_refresh_function),
    ]
