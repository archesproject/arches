import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "7125_geometry_index_table_update"),
    ]

    sql = """
        DROP VIEW IF EXISTS vw_annotations;

        CREATE OR REPLACE VIEW vw_annotations AS
        SELECT uuid(json_array_elements(t.tiledata::json->n.nodeid::text->'features')->>'id') AS feature_id,
            t.tileid,
            t.tiledata,
            t.resourceinstanceid,
            t.nodegroupid,
            n.nodeid,
            jsonb_array_elements(t.tiledata::jsonb->n.nodeid::text->'features') AS feature,
            json_array_elements(t.tiledata::json->n.nodeid::text->'features')->'properties'->>'canvas' AS canvas
        FROM tiles t
            LEFT JOIN nodes n ON t.nodegroupid = n.nodegroupid
        WHERE (
                (
                    SELECT count(*) AS count
                    FROM jsonb_object_keys(t.tiledata) jsonb_object_keys(jsonb_object_keys)
                    WHERE (
                            jsonb_object_keys.jsonb_object_keys IN (
                                SELECT n_1.nodeid::text AS nodeid
                                FROM nodes n_1
                                WHERE n_1.datatype = 'annotation'::text
                            )
                        )
                )
            ) > 0
        AND n.datatype = 'annotation'::text;
    """

    reverse_sql = """
        DROP VIEW IF EXISTS vw_annotations;

        CREATE OR REPLACE VIEW vw_annotations AS
        SELECT json_array_elements(t.tiledata::json->n.nodeid::text->'features')->>'id' AS feature_id,
            t.tileid,
            t.tiledata,
            t.resourceinstanceid,
            t.nodegroupid,
            n.nodeid,
            jsonb_array_elements(t.tiledata::jsonb->n.nodeid::text->'features') AS feature,
            json_array_elements(t.tiledata::json->n.nodeid::text->'features')->'properties'->>'canvas' AS canvas
        FROM tiles t
            LEFT JOIN nodes n ON t.nodegroupid = n.nodegroupid
        WHERE (
                (
                    SELECT count(*) AS count
                    FROM jsonb_object_keys(t.tiledata) jsonb_object_keys(jsonb_object_keys)
                    WHERE (
                            jsonb_object_keys.jsonb_object_keys IN (
                                SELECT n_1.nodeid::text AS nodeid
                                FROM nodes n_1
                                WHERE n_1.datatype = 'annotation'::text
                            )
                        )
                )
            ) > 0
        AND n.datatype = 'annotation'::text;
    """

    operations = [
        migrations.RunSQL(
            sql,
            reverse_sql,
        ),
    ]
