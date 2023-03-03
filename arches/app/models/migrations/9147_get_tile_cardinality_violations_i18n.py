from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("models", "9188_feature_annotation_type"),
    ]

    sql_string = """
create or replace function __arches_get_tile_cardinality_violations()
    returns table(graph_name text, node_names text[], resourceinstanceid uuid, nodegroupid uuid, parenttileid uuid, tilecount bigint) as
$$
DECLARE
    default_lang text;
BEGIN
    select code into default_lang from languages where isdefault limit 1;
    return query with tile_violations as ( SELECT t.resourceinstanceid,
                        t.nodegroupid,
                        t.parenttileid parent_tileid,
                        count(*)       tilecount
                 FROM tiles t,
                      node_groups ng
                 WHERE t.nodegroupid = ng.nodegroupid
                   AND ng.cardinality = '1'
                 group by t.resourceinstanceid, t.nodegroupid,
                          t.parenttileid
                 having count(*) > 1)
        select g.name->>default_lang,
               array_agg(n.name), tv.*
            from tile_violations tv,
                 nodes n,
                 graphs g
                where tv.nodegroupid = n.nodegroupid
                  and n.graphid = g.graphid
            group by g.name->>default_lang, tv.resourceinstanceid, tv.nodegroupid, tv.parent_tileid, tv.tilecount
    order by nodegroupid, resourceinstanceid;
END $$
    language plpgsql;

    """

    reverse_sql_string = """
create or replace function __arches_get_tile_cardinality_violations()
    returns table(graph_name text, node_names text[], resourceinstanceid uuid, nodegroupid uuid, parenttileid uuid, tilecount bigint) as
$$
DECLARE
BEGIN
    return query with tile_violations as ( SELECT t.resourceinstanceid,
                        t.nodegroupid,
                        t.parenttileid parent_tileid,
                        count(*)       tilecount
                 FROM tiles t,
                      node_groups ng
                 WHERE t.nodegroupid = ng.nodegroupid
                   AND ng.cardinality = '1'
                 group by t.resourceinstanceid, t.nodegroupid,
                          t.parenttileid
                 having count(*) > 1)
        select g.name, array_agg(n.name), tv.*
            from tile_violations tv,
                 nodes n,
                 graphs g
                where tv.nodegroupid = n.nodegroupid
                  and n.graphid = g.graphid
            group by g.name, tv.resourceinstanceid, tv.nodegroupid, tv.parent_tileid, tv.tilecount
    order by nodegroupid, resourceinstanceid;
END $$
    language plpgsql;
    """

    operations = [
        migrations.RunSQL(sql_string, reverse_sql_string),
    ]
