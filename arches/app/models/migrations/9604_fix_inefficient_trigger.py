from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("models", "8010_export_permissions"),
    ]

    update_check_excess_tiles_trigger = """
        DROP TRIGGER IF EXISTS __arches_check_excess_tiles_trigger ON tiles;
        DROP FUNCTION IF EXISTS __arches_check_excess_tiles_trigger_function();
        CREATE OR REPLACE FUNCTION __arches_check_excess_tiles_trigger_function()
        RETURNS trigger AS $$
        BEGIN
            IF (NEW.resourceinstanceid, NEW.nodegroupid, COALESCE(NEW.parenttileid::text, '')) IN (
                    SELECT t.resourceinstanceid, t.nodegroupid, COALESCE(t.parenttileid::text, '')
                    FROM tiles t, node_groups ng
                    WHERE t.nodegroupid = ng.nodegroupid
                    AND ng.cardinality = '1'
                    AND t.resourceinstanceid = NEW.resourceinstanceid 
                ) THEN
                    RAISE EXCEPTION 'Multiple Tiles for Cardinality-1 Nodegroup | nodegroupid: %, resourceinstanceid: %, parenttileid: %', NEW.nodegroupid, NEW.resourceinstanceid, COALESCE(NEW.parenttileid::text, 'root')  USING ERRCODE = '21000';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER __arches_check_excess_tiles_trigger
            BEFORE INSERT ON tiles
            FOR EACH ROW
            EXECUTE PROCEDURE __arches_check_excess_tiles_trigger_function();
        """

    restore_check_excess_tiles_trigger = """
        DROP TRIGGER IF EXISTS __arches_check_excess_tiles_trigger ON tiles;
        DROP FUNCTION IF EXISTS __arches_check_excess_tiles_trigger_function();
        CREATE OR REPLACE FUNCTION __arches_check_excess_tiles_trigger_function()
        RETURNS trigger AS $$
        BEGIN
            IF (NEW.resourceinstanceid, NEW.nodegroupid, COALESCE(NEW.parenttileid::text, '')) IN (
                    SELECT t.resourceinstanceid, t.nodegroupid, COALESCE(t.parenttileid::text, '')
                    FROM tiles t, node_groups ng
                    WHERE t.nodegroupid = ng.nodegroupid
                    AND ng.cardinality = '1'
                ) THEN
                    RAISE EXCEPTION 'Multiple Tiles for Cardinality-1 Nodegroup | nodegroupid: %, resourceinstanceid: %, parenttileid: %', NEW.nodegroupid, NEW.resourceinstanceid, COALESCE(NEW.parenttileid::text, 'root')  USING ERRCODE = '21000';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER __arches_check_excess_tiles_trigger
            BEFORE INSERT ON tiles
            FOR EACH ROW
            EXECUTE PROCEDURE __arches_check_excess_tiles_trigger_function();
        """

    operations = [
        migrations.RunSQL(
            update_check_excess_tiles_trigger, restore_check_excess_tiles_trigger
        ),
    ]
