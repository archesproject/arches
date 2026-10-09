from django.contrib.postgres.fields import ArrayField
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "12913_remove_geocoders"),
    ]

    create_spatial_view_with_grants = """
            CREATE OR REPLACE FUNCTION public.__arches_create_spatial_view(
                spatial_view_name_slug text,
                geometry_node_id uuid,
                attribute_node_list jsonb,
                schema_name text DEFAULT 'public'::text,
                spv_description text DEFAULT 'arches spatial view'::text,
                is_mixed_geometry_type boolean DEFAULT false,
                language_id text DEFAULT 'en')
                RETURNS boolean
                LANGUAGE 'plpgsql'
                COST 100
                VOLATILE STRICT PARALLEL UNSAFE
            AS $BODY$
                            declare
                                sv_name_slug_with_geom    text;
                                success                   boolean := false;
                                sv_create                 text := '';
                                att_table_name            text;
                                g                         record;
                                n						  record;
                                geom_list				  text := '';
                                geom_type_filter          text;
                                sv_names                  text[] := '{}';
                                r                         record;
                            begin
                                att_table_name := __arches_create_spatial_view_attribute_table(spatial_view_name_slug, geometry_node_id, attribute_node_list, schema_name, language_id);
                                if att_table_name = 'error' then
                                    return success;
                                end if;

                                if is_mixed_geometry_type = false then
                                    geom_list := 'ST_Point,ST_LineString,ST_Polygon';
                                else
                                    geom_list := 'mixed_geom';
                                end if;

                                for g in 
                                    select unnest(string_to_array(geom_list,',')) as geometry_type
                                loop
                                    if g.geometry_type = 'mixed_geom' then
                                        geom_type_filter := '';
                                    else
                                        geom_type_filter := format('and ST_GeometryType(geo.geom) = ''%s''',g.geometry_type);
                                    end if;
                                    
                                    sv_name_slug_with_geom := format('%s.%s_%s',schema_name, spatial_view_name_slug, lower(replace(g.geometry_type,'ST_','')));
                                    sv_names := sv_names || sv_name_slug_with_geom;

                                    sv_create := sv_create || 
                                        format('
                                        create or replace view %s AS
                                        select 
                                            geo.id AS gid,
                                            geo.tileid::text AS tileid, 
                                            geo.nodeid::text AS nodeid,
                                            geo.geom,
                                            att.*
                                            FROM public.geojson_geometries geo
                                                join %s att ON geo.resourceinstanceid::text = att.resourceinstanceid::text
                                        where geo.nodeid = ''%s''
                                            %s;

                                        comment on view %s is ''%s'';

                                        ',
                                        sv_name_slug_with_geom,
                                        att_table_name,
                                        geometry_node_id::text,
                                        geom_type_filter,
                                        sv_name_slug_with_geom,
                                        spv_description);

                                        sv_create = sv_create || format(
                                                        'comment on column %s.%s is ''%s'';',
                                                        sv_name_slug_with_geom,
                                                        'gid',
                                                        'Unique geometry id. This is not guarenteed to be consistent across sessions.'
                                                        );
                                                        
                                        sv_create = sv_create || format(
                                                        'comment on column %s.%s is ''%s'';',
                                                        sv_name_slug_with_geom,
                                                        'resourceinstanceid',
                                                        'Globally unique Arches resource ID'
                                                        );
                                        sv_create = sv_create || format(
                                                        'comment on column %s.%s is ''%s'';',
                                                        sv_name_slug_with_geom,
                                                        'nodeid',
                                                        'Id for the Arches graph node containing the geometry'
                                                        );
                                                        
                                        sv_create = sv_create || format(
                                                        'comment on column %s.%s is ''%s'';',
                                                        sv_name_slug_with_geom,
                                                        'tileid',
                                                        'Id of the tile record storing the geometry'
                                                        );

                                        for n in
                                            with attribute_nodes as (
                                                select * from jsonb_to_recordset(attribute_node_list) as x(nodeid uuid, description text)
                                            )
                                            select 
                                                __arches_slugify(n1.alias) as alias, 
                                                n1.nodeid, 
                                                n1.nodegroupid,
                                                att_nodes.description
                                            from nodes n1
                                                join (select * from attribute_nodes) att_nodes ON n1.nodeid = att_nodes.nodeid
                                        loop
                                            sv_create := sv_create || 
                                                format('
                                                    comment on column %s.%s is ''%s'';
                                                ',
                                                sv_name_slug_with_geom,
                                                n.alias,
                                                n.description);
                                        end loop;

                                end loop;
                                
                                execute sv_create;

                                -- grant read access to the view's existing database roles
                                for r in
                                    select pr.rolname, v.view_name
                                    from spatial_views sv
                                        cross join unnest(sv.dbroles) as dr(rolname)
                                        join pg_roles pr on pr.rolname = dr.rolname
                                        cross join unnest(sv_names) as v(view_name)
                                    where sv.slug = spatial_view_name_slug
                                        and sv.schema = schema_name
                                loop
                                    execute format('grant select on %s to %I;', r.view_name, r.rolname);
                                end loop;
                                
                                success := true;
                                
                                return success;
                            end;
                            
            $BODY$;
        """

    create_spatial_view_without_grants = """
            CREATE OR REPLACE FUNCTION public.__arches_create_spatial_view(
                spatial_view_name_slug text,
                geometry_node_id uuid,
                attribute_node_list jsonb,
                schema_name text DEFAULT 'public'::text,
                spv_description text DEFAULT 'arches spatial view'::text,
                is_mixed_geometry_type boolean DEFAULT false,
                language_id text DEFAULT 'en')
                RETURNS boolean
                LANGUAGE 'plpgsql'
                COST 100
                VOLATILE STRICT PARALLEL UNSAFE
            AS $BODY$
                            declare
                                sv_name_slug_with_geom    text;
                                success                   boolean := false;
                                sv_create                 text := '';
                                att_table_name            text;
                                g                         record;
                                n						  record;
                                geom_list				  text := '';
                                geom_type_filter          text;
                            begin
                                att_table_name := __arches_create_spatial_view_attribute_table(spatial_view_name_slug, geometry_node_id, attribute_node_list, schema_name, language_id);
                                if att_table_name = 'error' then
                                    return success;
                                end if;

                                if is_mixed_geometry_type = false then
                                    geom_list := 'ST_Point,ST_LineString,ST_Polygon';
                                else
                                    geom_list := 'mixed_geom';
                                end if;

                                for g in 
                                    select unnest(string_to_array(geom_list,',')) as geometry_type
                                loop
                                    if g.geometry_type = 'mixed_geom' then
                                        geom_type_filter := '';
                                    else
                                        geom_type_filter := format('and ST_GeometryType(geo.geom) = ''%s''',g.geometry_type);
                                    end if;
                                    
                                    sv_name_slug_with_geom := format('%s.%s_%s',schema_name, spatial_view_name_slug, lower(replace(g.geometry_type,'ST_','')));

                                    sv_create := sv_create || 
                                        format('
                                        create or replace view %s AS
                                        select 
                                            geo.id AS gid,
                                            geo.tileid::text AS tileid, 
                                            geo.nodeid::text AS nodeid,
                                            geo.geom,
                                            att.*
                                            FROM public.geojson_geometries geo
                                                join %s att ON geo.resourceinstanceid::text = att.resourceinstanceid::text
                                        where geo.nodeid = ''%s''
                                            %s;

                                        comment on view %s is ''%s'';

                                        ',
                                        sv_name_slug_with_geom,
                                        att_table_name,
                                        geometry_node_id::text,
                                        geom_type_filter,
                                        sv_name_slug_with_geom,
                                        spv_description);

                                        sv_create = sv_create || format(
                                                        'comment on column %s.%s is ''%s'';',
                                                        sv_name_slug_with_geom,
                                                        'gid',
                                                        'Unique geometry id. This is not guarenteed to be consistent across sessions.'
                                                        );
                                                        
                                        sv_create = sv_create || format(
                                                        'comment on column %s.%s is ''%s'';',
                                                        sv_name_slug_with_geom,
                                                        'resourceinstanceid',
                                                        'Globally unique Arches resource ID'
                                                        );
                                        sv_create = sv_create || format(
                                                        'comment on column %s.%s is ''%s'';',
                                                        sv_name_slug_with_geom,
                                                        'nodeid',
                                                        'Id for the Arches graph node containing the geometry'
                                                        );
                                                        
                                        sv_create = sv_create || format(
                                                        'comment on column %s.%s is ''%s'';',
                                                        sv_name_slug_with_geom,
                                                        'tileid',
                                                        'Id of the tile record storing the geometry'
                                                        );

                                        for n in
                                            with attribute_nodes as (
                                                select * from jsonb_to_recordset(attribute_node_list) as x(nodeid uuid, description text)
                                            )
                                            select 
                                                __arches_slugify(n1.alias) as alias, 
                                                n1.nodeid, 
                                                n1.nodegroupid,
                                                att_nodes.description
                                            from nodes n1
                                                join (select * from attribute_nodes) att_nodes ON n1.nodeid = att_nodes.nodeid
                                        loop
                                            sv_create := sv_create || 
                                                format('
                                                    comment on column %s.%s is ''%s'';
                                                ',
                                                sv_name_slug_with_geom,
                                                n.alias,
                                                n.description);
                                        end loop;

                                end loop;
                                
                                execute sv_create;
                                
                                success := true;
                                
                                return success;
                            end;
                            
            $BODY$;
        """

    # keep access for databases where earlier migrations created the legacy role
    preserve_legacy_role = """
            alter table spatial_views disable trigger user;

            update spatial_views
            set dbroles = array['arches_spatial_views']
            where exists (
                select from pg_catalog.pg_roles
                where rolname = 'arches_spatial_views'
            );

            alter table spatial_views enable trigger user;
        """

    operations = [
        migrations.AddField(
            model_name="spatialview",
            name="dbroles",
            field=ArrayField(
                base_field=models.CharField(max_length=63),
                blank=True,
                db_default=[],
                default=list,
                size=None,
            ),
        ),
        migrations.RunSQL(
            create_spatial_view_with_grants, create_spatial_view_without_grants
        ),
        migrations.RunSQL(preserve_legacy_role, migrations.RunSQL.noop),
    ]
