from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "8009_etlmodule"),
    ]
    operations = [
        migrations.RunSQL(
            sql="""
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

            """,
            reverse_sql="""
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
                from relationships;

                return true;
            end;
            $$ language plpgsql;

            """,
        )
    ]
