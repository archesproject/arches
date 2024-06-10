from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("models", "9892_tile_excel_exporter"),
    ]

    update_refresh_tile_resource_relationship_function = (
        """
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
    """,
    )

    revert_refresh_tile_resource_relationship_function = """
        create or replace function __arches_refresh_tile_resource_relationships(
            tile_id uuid
        ) returns boolean as $$
        declare
            resource_id uuid;
        begin
            select resourceinstanceid into resource_id from tiles where tileid = tile_id;

            delete from resource_x_resource where tileid = tile_id;

            with relationships as (
                select n.nodeid,
                    jsonb_array_elements(t.tiledata->n.nodeid::text) as relationship
                from tiles t
                    left join nodes n on t.nodegroupid = n.nodegroupid
                where n.datatype in ('resource-instance-list', 'resource-instance')
                    and t.tileid = tile_id
                    and t.tiledata->>n.nodeid::text is not null
            )
            insert into resource_x_resource (
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
            ) select
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
            from relationships;

            return true;
        end;
        $$ language plpgsql;
    """

    update_previous_relationship = """
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
    """

    operations = [
        migrations.RunSQL(
            update_refresh_tile_resource_relationship_function,
            revert_refresh_tile_resource_relationship_function,
        ),
        migrations.RunSQL(
            update_previous_relationship,
            migrations.RunSQL.noop,
        ),
    ]
