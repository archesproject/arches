from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("models", "8502_loadevent_indexed_time"),
    ]

    sql_string = """
    create procedure __arches_prepare_bulk_load() as
    $$
    DECLARE
    BEGIN
        alter table tiles disable trigger __arches_check_excess_tiles_trigger;
        alter table tiles disable trigger __arches_trg_update_spatial_attributes;
        Raise Notice 'tiles triggers disabled.';
        Raise Notice ' run __arches_complete_bulk_load after loads complete to re-enable triggers and refresh spatial views';
    END $$
    language plpgsql;

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
            Raise Exception 'Cardinality violations found. Run `select * from __arches_get_tile_cardinality_violations()` to list violations';
        else
            Raise Notice 'No cardinality violations found';
        end if;
    END $$
    language plpgsql;

    create or replace function __arches_get_tile_cardinality_violations()
        returns table(resourceinstanceid uuid, nodegroupid uuid, parenttileid uuid, tilecount bigint) as
    $$
    DECLARE
    BEGIN
        return query SELECT t.resourceinstanceid,
                            t.nodegroupid,
                            COALESCE(t.parenttileid::text, '')::uuid parent_tileid,
                            count(*)                           tilecount
                     FROM tiles t,
                          node_groups ng
                     WHERE t.nodegroupid = ng.nodegroupid
    --                                       AND ng.nodegroupid in (select n.nodegroupid from nodes n where n.graphid = (select graphid from graphs g where g.name = 'BC Fossil Site'))
                       AND ng.cardinality = '1'
                     group by t.resourceinstanceid, t.nodegroupid,
                              COALESCE(t.parenttileid::text, '')
                     having count(*) > 1
        order by nodegroupid, resourceinstanceid;
    END $$
        language plpgsql;

    """

    reverse_sql_string = """
    drop procedure __arches_prepare_bulk_load;
    drop procedure __arches_complete_bulk_load;
    drop function __arches_get_tile_cardinality_violations;
    """

    operations = [
        migrations.RunSQL(sql_string, reverse_sql_string),
    ]
