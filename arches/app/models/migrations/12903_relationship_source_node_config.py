from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("models", "12779_add_multicard_resource_descriptor"),
    ]

    # Collapse the four relationship keys on each entry of a resource-instance node's
    # config.graphs into a single discriminator plus one pair of values, so that a
    # relationship type can also be drawn from a controlled list:
    #   useOntologyRelationship  -> relationshipSource ('ontology-property'|'concept'|'reference')
    #   ontologyProperty         -> relationship
    #   inverseOntologyProperty  -> inverseRelationship
    #   relationshipConcept      -> relationship
    #   inverseRelationshipConcept -> inverseRelationship
    # Tile values keep ontologyProperty/inverseOntologyProperty; only node configs change.
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
                    CASE WHEN element->>'useOntologyRelationship' = 'true'
                        THEN 'ontology-property' ELSE 'concept' END,
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

    """
    Reversing the rewrite of a property in a nested array means disassembling and reassembling
    the object. see https://stackoverflow.com/a/58802637
    Because the new properties are inert in prior versions of Arches and because of the possible
    complexity of these configs, there is a chance of rebuilding node configs incorrectly in a
    reverse migration, so the reverse migration leaves them in place.
    """
    reverse_node_configs = ""

    # The node config defaults read by this function move with the keys above. The COALESCE
    # keeps configs that have not been rewritten (eg. a graph imported from an older package)
    # working. The tile-level reads are unchanged.
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

    operations = [
        migrations.RunSQL(update_node_configs, reverse_node_configs),
        migrations.RunSQL(update_relationship_function, reverse_relationship_function),
    ]
