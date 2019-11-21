from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("models", "5564_export_ui")]

    operations = [
        migrations.RunSQL(
            """
            DROP MATERIALIZED VIEW mv_geojson_geoms;
            CREATE MATERIALIZED VIEW mv_geojson_geoms AS
                SELECT t.tileid,
                    t.resourceinstanceid,
                    n.nodeid,
                    ST_Transform(ST_SetSRID(
                       st_geomfromgeojson(
                           (
                               json_array_elements(
                                   t.tiledata::json ->
                                   n.nodeid::text ->
                               'features') -> 'geometry'
                           )::text
                       ),
                       4326
                   ), 3857) AS geom
                FROM tiles t
                LEFT JOIN nodes n ON t.nodegroupid = n.nodegroupid
                WHERE n.datatype = 'geojson-feature-collection'::text;

            CREATE INDEX mv_geojson_geoms_gix ON mv_geojson_geoms USING GIST (geom);
            """,
            """
            DROP MATERIALIZED VIEW mv_geojson_geoms;
            CREATE MATERIALIZED VIEW mv_geojson_geoms AS
                SELECT t.tileid,
                    t.resourceinstanceid,
                    n.nodeid,
                    st_transform(
                        ST_SetSRID(
                            st_geomfromgeojson(
                                (json_array_elements(t.tiledata::json -> n.nodeid::text -> 'features') -> 'geometry')::text
                            ),
                        4326
                    ), 900913)::geometry(Geometry,900913) AS geom
                FROM tiles t
                LEFT JOIN nodes n ON t.nodegroupid = n.nodegroupid
                WHERE (( SELECT count(*) AS count
                    FROM jsonb_object_keys(t.tiledata) jsonb_object_keys(jsonb_object_keys)
                    WHERE (jsonb_object_keys.jsonb_object_keys IN ( SELECT n_1.nodeid::text AS nodeid
                    FROM nodes n_1
                    WHERE n_1.datatype = 'geojson-feature-collection'::text)))) > 0 AND n.datatype = 'geojson-feature-collection'::text;

            CREATE INDEX mv_geojson_geoms_gix ON mv_geojson_geoms USING GIST (geom);
            """,
        )
    ]
