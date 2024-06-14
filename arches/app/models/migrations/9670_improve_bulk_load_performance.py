from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("models", "9648_add_empty_key_value_pairs_to_tiles"),
    ]

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
        create or replace procedure __arches_complete_bulk_load() as
        $$
        DECLARE
            cardinality_violations bigint;
        BEGIN
            alter table tiles enable trigger __arches_check_excess_tiles_trigger;
            alter table tiles enable trigger __arches_trg_update_spatial_attributes;

            if (not __arches_refresh_spatial_views()) then
                Raise EXCEPTION 'Unable to refresh spatial views';
            end if;

        with cardinality_violations as (SELECT t.resourceinstanceid,
                                                t.nodegroupid,
                                                COALESCE(t.parenttileid::text, '') parent_tileid,
                                                count(*)
                                        FROM tiles t,
                                                node_groups ng
                                        WHERE t.nodegroupid = ng.nodegroupid
                                            AND ng.cardinality = '1'
                                        group by t.resourceinstanceid, t.nodegroupid, parent_tileid
                                        having count(*) > 1)
        select count(*)
        into cardinality_violations
        from cardinality_violations;

            if (cardinality_violations > 0) then
                Raise Exception 'Cardinality violations found. Run `%` to list violations',
                    'select * from __arches_get_tile_cardinality_violations()';
            else
                Raise Notice 'No cardinality violations found';
            end if;
        END $$
        language plpgsql;
    """

    create_index_on_load_staging_tileid = """
        CREATE INDEX IF NOT EXISTS load_staging_tileid ON load_staging (tileid);
    """

    drop_index_on_load_staging_tileid = """
        DROP INDEX IF EXISTS load_staging_tileid;
    """

    operations = [
        migrations.RunSQL(
            update_check_excess_tiles_trigger, restore_check_excess_tiles_trigger
        ),
        migrations.RunSQL(
            create_index_on_load_staging_tileid, drop_index_on_load_staging_tileid
        ),
    ]
