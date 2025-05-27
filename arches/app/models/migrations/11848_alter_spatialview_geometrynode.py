import django.db.models.deletion
from django.db import migrations, models
import pgtrigger


class Migration(migrations.Migration):
    drop_legacy_trigger = "drop trigger if exists __arches_trg_update_spatial_views on spatial_views; drop function if exists __arches_trg_fnc_update_spatial_views;"

    create_legacy_trigger = """
        CREATE OR REPLACE FUNCTION public.__arches_trg_fnc_update_spatial_views()
            RETURNS trigger
            LANGUAGE 'plpgsql'
            COST 100
            VOLATILE NOT LEAKPROOF
        AS $BODY$
            declare
                sv_perform text := '';
                valid_geom_nodeid boolean := false;
                has_att_nodes integer := 0;
                valid_att_nodeids boolean := false;
                valid_language_count integer := 0;
            begin
                if tg_op = 'INSERT' or tg_op = 'UPDATE' then
                    valid_geom_nodeid := (select count(*) from nodes where nodeid = new.geometrynodeid and datatype = 'geojson-feature-collection') > 0;
                    if valid_geom_nodeid is false then
                        raise exception 'geometrynodeid is not a valid nodeid';
                    end if;


                    if jsonb_typeof(new.attributenodes::jsonb) = 'array' then
                        has_att_nodes := jsonb_array_length(new.attributenodes);
                        if has_att_nodes = 0 then
                            raise exception 'attributenodes needs at least one attribute dict';
                        else
                            valid_att_nodeids := (
                                with attribute_nodes as (
                                    select * from jsonb_to_recordset(new.attributenodes) as x(nodeid uuid, description text)
                                )
                                select count(*) from attribute_nodes att join nodes n1 on att.nodeid = n1.nodeid
                                ) > 0;

                            if valid_att_nodeids is false then
                                raise exception 'attributenodes contains an invalid nodeid';
                            end if;
                        end if;
                    else
                        raise exception 'attributenodes needs to be an array';
                    end if;
                    ----------------------------------------------------------------------------------------------
                    -- check language code is valid
                    select count(pg.languageid)
                    into valid_language_count
                    from published_graphs pg
                        join graphs_x_published_graphs gxpg on pg.publicationid = gxpg.publicationid
                        join graphs g on gxpg.publicationid = g.publicationid
                    where g.graphid in (select graphid from nodes where nodeid = new.geometrynodeid)
                        and pg.languageid = new.languageid;

                    if valid_language_count = 0 then
                        raise exception 'language is not valid for this graph';
                    end if;

                end if;


                if tg_op = 'DELETE' then
                    sv_perform := sv_perform || format(
                        'select __arches_delete_spatial_view(%L,%L);'
                        , old.slug
                        , old.schema);

                    if sv_perform <> '' then
                        execute sv_perform;
                    end if;

                    return old;

                elsif tg_op = 'INSERT' then
                    if new.isactive = true then
                        sv_perform := sv_perform || format(
                            'select __arches_create_spatial_view(%L, %L::uuid, %L::jsonb, %L, %L, %L, %L);'
                            , new.slug
                            , new.geometrynodeid
                            , new.attributenodes
                            , new.schema
                            , new.description
                            , new.ismixedgeometrytypes
                            , new.languageid);
                    end if;

                    if sv_perform <> '' then
                        execute sv_perform;
                    end if;

                    return new;

                elsif tg_op = 'UPDATE' then

                    if new.isactive = true then
                        sv_perform := sv_perform || format(
                            'select __arches_update_spatial_view(%L, %L, %L, %L::uuid, %L::jsonb, %L, %L, %L);'
                            , old.slug
                            , old.schema
                            , new.slug
                            , new.geometrynodeid
                            , new.attributenodes
                            , new.schema
                            , new.description
                            , new.ismixedgeometrytypes
                            , new.languageid);
                    else
                        sv_perform := sv_perform || format(
                            'select __arches_delete_spatial_view(%L,%L);'
                            , old.slug
                            , old.schema);
                    end if;

                    if sv_perform <> '' then
                        execute sv_perform;
                    end if;

                    return new;
                end if;
            end;
            $BODY$;

            create constraint trigger __arches_trg_update_spatial_views
            after insert or update or delete
            on spatial_views
            deferrable initially deferred
            for each row
                execute procedure __arches_trg_fnc_update_spatial_views();
    """

    dependencies = [
        ("models", "11800_remove_foreign_object"),
    ]

    operations = [
        migrations.RunSQL(drop_legacy_trigger, create_legacy_trigger),
        pgtrigger.migrations.AddTrigger(
            model_name="spatialview",
            trigger=pgtrigger.compiler.Trigger(
                name="arches_update_spatial_views",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    declare="DECLARE sv_perform text; valid_geom_nodeid boolean; has_att_nodes integer; valid_att_nodeids boolean; valid_language_count integer;",
                    func="\nsv_perform := '';\nvalid_geom_nodeid := false;\nhas_att_nodes := 0;\nvalid_att_nodeids := false;\nvalid_language_count := 0;\n\nif tg_op = 'INSERT' or tg_op = 'UPDATE' then\n    valid_geom_nodeid := (select count(*) from nodes where nodeid = new.geometrynodeid and datatype = 'geojson-feature-collection') > 0;\n    if valid_geom_nodeid is false then\n        raise exception 'geometrynodeid is not a valid nodeid';\n    end if;\n\n\n    if jsonb_typeof(new.attributenodes::jsonb) = 'array' then\n        has_att_nodes := jsonb_array_length(new.attributenodes);\n        if has_att_nodes = 0 then\n            raise exception 'attributenodes needs at least one attribute dict';\n        else\n            valid_att_nodeids := (\n                with attribute_nodes as (\n                    select * from jsonb_to_recordset(new.attributenodes) as x(nodeid uuid, description text)\n                )\n                select count(*) from attribute_nodes att join nodes n1 on att.nodeid = n1.nodeid\n                ) > 0;\n\n            if valid_att_nodeids is false then\n                raise exception 'attributenodes contains an invalid nodeid';\n            end if;\n        end if;\n    else\n        raise exception 'attributenodes needs to be an array';\n    end if;\nend if;\n\n\nif tg_op = 'DELETE' then\n    sv_perform := sv_perform || format(\n        'select __arches_delete_spatial_view(%L,%L);'\n        , old.slug\n        , old.schema);\n\n    if sv_perform <> '' then\n        execute sv_perform;\n    end if;\n\n    return old;\n\nelsif tg_op = 'INSERT' then\n    if new.isactive = true then\n        sv_perform := sv_perform || format(\n            'select __arches_create_spatial_view(%L, %L::uuid, %L::jsonb, %L, %L, %L, %L);'\n            , new.slug\n            , new.geometrynodeid\n            , new.attributenodes\n            , new.schema\n            , new.description\n            , new.ismixedgeometrytypes\n            , new.languageid);\n    end if;\n\n    if sv_perform <> '' then\n        execute sv_perform;\n    end if;\n\n    return new;\n\nelsif tg_op = 'UPDATE' then\n\n    if new.isactive = true then\n        sv_perform := sv_perform || format(\n            'select __arches_update_spatial_view(%L, %L, %L, %L::uuid, %L::jsonb, %L, %L, %L);'\n            , old.slug\n            , old.schema\n            , new.slug\n            , new.geometrynodeid\n            , new.attributenodes\n            , new.schema\n            , new.description\n            , new.ismixedgeometrytypes\n            , new.languageid);\n    else\n        sv_perform := sv_perform || format(\n            'select __arches_delete_spatial_view(%L,%L);'\n            , old.slug\n            , old.schema);\n    end if;\n\n    if sv_perform <> '' then\n        execute sv_perform;\n    end if;\n\n    return new;\nend if;\n",
                    hash="cc340ca6f102932bc957c60a1340aeb5512295d5",
                    operation="UPDATE OR DELETE OR INSERT",
                    pgid="pgtrigger_arches_update_spatial_views_ebfdd",
                    table="spatial_views",
                    when="AFTER",
                ),
            ),
        ),
    ]
