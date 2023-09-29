from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('models', '10041_limit_number_of_bulk_edit'),
    ]

    update_refresh_tile_resource_relationship_function = """
        CREATE OR REPLACE FUNCTION __arches_refresh_tile_resource_relationships(tile_id uuid)
        RETURNS boolean AS $$
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
        $$ language plpgsql;
    """,

    revert_refresh_tile_resource_relationship_function = """
        CREATE OR REPLACE FUNCTION __arches_refresh_tile_resource_relationships(tile_id uuid)
        RETURNS boolean AS $$
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
                modified
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
                now()
            FROM relationships;

            UPDATE resource_x_resource x
            SET resourceinstancefrom_graphid = r.graphid
            FROM resource_instances r
            WHERE r.resourceinstanceid = x.resourceinstanceidfrom
            AND x.resourceinstancefrom_graphid is null;

            UPDATE resource_x_resource x
            SET resourceinstanceto_graphid = r.graphid
            FROM resource_instances r
            WHERE r.resourceinstanceid = x.resourceinstanceidto
            AND x.resourceinstanceto_graphid is null;

            RETURN true;
        END;
        $$ language plpgsql;
    """

    update_check_excess_tiles_trigger = """
        create or replace procedure __arches_complete_bulk_load() AS
        $$
            DECLARE
                cardinality_violations bigint;
            BEGIN
                alter table tiles enable trigger __arches_check_excess_tiles_trigger;
                alter table tiles enable trigger __arches_trg_update_spatial_attributes;
            END
        $$
        language plpgsql;
    """

    restore_check_excess_tiles_trigger = """
        create or replace procedure __arches_complete_bulk_load() AS
        $$
            DECLARE
                cardinality_violations bigint;
            BEGIN
                alter table tiles enable trigger __arches_check_excess_tiles_trigger;
                alter table tiles enable trigger __arches_trg_update_spatial_attributes;
            END
        $$
        language plpgsql;
    """


    operations = [
        migrations.RunSQL(update_check_excess_tiles_trigger, restore_check_excess_tiles_trigger),
    ]


    operations = [
        migrations.RunSQL(
            update_refresh_tile_resource_relationship_function,
            revert_refresh_tile_resource_relationship_function,
        ),
        migrations.RunSQL(
            update_check_excess_tiles_trigger,
            restore_check_excess_tiles_trigger
        ),
    ]
