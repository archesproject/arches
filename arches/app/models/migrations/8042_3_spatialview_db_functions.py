from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("models", "8042_2_spatialview_model"),
    ]

    sql_string = """
            do
            $do$
            declare
                database_name     text;
                sv_user_sql     text;
            begin
                if not exists (
                    select from pg_catalog.pg_roles
                    where  rolname = 'arches_spatial_views') then

                    select current_database() into database_name;

                    create role arches_spatial_views with
                    login
                    nosuperuser
                    inherit
                    nocreatedb
                    nocreaterole
                    noreplication
                    password 'arches_spatial_views';

                    sv_user_sql := format('grant connect on database %s to arches_spatial_views;', database_name);
                    execute sv_user_sql;

                end if;
            end
            $do$;

            create or replace function __arches_get_concept_label(concept_value uuid) returns text language plpgsql as $$
                declare
                    concept_label     text := '';
                begin
                    if concept_value is null then
                        return concept_label;
                    end if;

                    select v.value
                    into concept_label
                    from values v
                    where v.valueid = concept_value::uuid;

                    if concept_label is null then
                        concept_label := '';
                    end if;
                    
                return concept_label;
                end;
                $$;

            create or replace function __arches_get_concept_list_label(concept_array jsonb) returns text language plpgsql as $$
                declare
                    concept_list     text := '';
                begin
                    if concept_array is null or concept_array::text = 'null' then
                        return concept_list;
                    end if;

                    select string_agg(d.label, ', ')
                    from
                    (
                        select __arches_get_concept_label(x.conceptid::uuid) as label
                        from (select json_array_elements_text(concept_array::json) as conceptid) x
                    ) d
                    into concept_list;
                    
                    if (concept_list is null) then
                        concept_list := '';
                    end if;
                
                return concept_list;
                end;
                $$;

            create or replace function __arches_get_domain_label(domain_value uuid, in_nodeid uuid) returns text language plpgsql as $$
                declare
                    in_node_config      jsonb;
                    return_label        text;
                begin
                    if domain_value is null or in_nodeid is null then
                        return '';
                    end if;    

                    select n.config
                    into in_node_config
                    from nodes n
                    where n.nodeid = in_nodeid::uuid;

                    select (opt ->> 'text')
                    into return_label
                    from (select jsonb_array_elements(in_node_config -> 'options') AS opt) opts
                    where (opt ->> 'id') = domain_value::text;
                    
                    if return_label is null then
                        return_label = '';
                    end if;
                    
                return return_label;
                end;
                $$;


            create or replace function __arches_get_domain_list_label(domain_value_list jsonb, in_nodeid uuid) returns text language plpgsql as $$
                declare
                    return_label     text := '';
                begin
                    if domain_value_list is null or in_nodeid is null then
                        return '';
                    end if;
                    
                    select string_agg(dvl.label, ', ')
                    from
                    (
                        select __arches_get_domain_label(dv.domain_value::uuid, in_nodeid) as label
                        from (
                            select jsonb_array_elements_text(domain_value_list) as domain_value
                        ) dv
                    ) dvl
                    into return_label;
                    
                return return_label;
                end;
                $$;


            create or replace function __arches_get_resourceinstance_label(resourceinstance_value jsonb, label_type text default 'name') returns text language plpgsql as $$
                declare
                    return_label                 text := '';
                    target_resourceinstanceid     uuid;
                    target_graph_funct_config     jsonb;
                    target_graphid                 uuid;
                    target_nodegroupid             uuid;
                    target_template             text;
                    target_tiledata             jsonb;
                    target_provisionaledits     jsonb;
                    target_data                 jsonb;
                begin

                    if resourceinstance_value is null or resourceinstance_value::text = 'null' then
                        return return_label;
                    end if;
                    
                    target_resourceinstanceid := ((resourceinstance_value -> 0) ->> 'resourceId')::uuid;
                    if target_resourceinstanceid is null then
                        target_resourceinstanceid := (resourceinstance_value ->> 'resourceId')::uuid;
                    end if;
                    if target_resourceinstanceid is null then
                        return return_label;
                    end if;
                    
                    
                    select r.graphid
                    into target_graphid
                    from resource_instances r
                    where resourceinstanceid = target_resourceinstanceid;
                    
                    select fxg.config -> 'descriptor_types'
                    into target_graph_funct_config
                    from functions_x_graphs fxg
                    join functions f on fxg.functionid = f.functionid
                    where f.functiontype = 'primarydescriptors'
                        AND fxg.graphid = target_graphid;
                    
                    if target_graph_funct_config is null then
                        raise notice 'target_graph_funct_config is null for graphid (%)', target_graphid;
                        raise notice '...resourceid was (%)', target_resourceinstanceid::text;
                        return return_label;
                    end if;
                    

                    if jsonb_path_exists(target_graph_funct_config, format('$.%s.nodegroup_id',label_type)::jsonpath) then
                        target_nodegroupid := (target_graph_funct_config::json #>> format('{%s,nodegroup_id}',label_type)::text[])::uuid;
                        if target_nodegroupid::text = '' then
                            raise notice 'target_nodegroupid is an empty string';
                            return return_label;
                        end if;                    
                    end if;
                    
                    if jsonb_path_exists(target_graph_funct_config, format('$.%s.string_template',label_type)::jsonpath) then
                        target_template := (target_graph_funct_config::json #>> format('{%s,string_template}',label_type)::text[])::text;
                        if target_template::text = '' then
                            raise notice 'target_template is an empty string';
                            return return_label;
                        end if;                    
                    end if;
                    
                    select t.tiledata, t.provisionaledits
                    into target_tiledata, target_provisionaledits
                    from tiles t
                    where t.nodegroupid = target_nodegroupid
                        and t.resourceinstanceid = target_resourceinstanceid
                    order by t.sortorder nulls last
                    limit 1;

                    if target_tiledata is null and target_provisionaledits is null then
                        return return_label;
                    end if;

                    target_data := '{}'::jsonb;
                    
                    declare
                        tiledata_keycount                 integer := 0;
                        provisionaledits_users_keycount integer := 0;
                        provisionaledits_userid         text;
                    begin
                        select count(*) from jsonb_object_keys(target_tiledata) into tiledata_keycount;
                        if tiledata_keycount > 0 then
                            target_data := target_tiledata;
                        else
                            if target_provisionaledits is not null then
                                select count(*) from jsonb_object_keys(target_provisionaledits) into provisionaledits_users_keycount;
                                if provisionaledits_users_keycount == 1 then
                                    select u.userid::text from (select userid FROM json_each_text(data) LIMIT 1) u into provisionaledits_userid;
                                    target_data := (target_provisionaledits ->> userid)::jsonb;
                                end if;
                            end if;
                        end if;
                    end;    
                    
                    declare
                        n record;
                    begin
                        for n in select *
                            from nodes
                            where nodegroupid = target_nodegroupid
                        loop
                            if target_template like format('%%<%s>%%',n.name) then
                                select replace(target_template, format('<%s>',n.name), __arches_get_node_display_value(target_data, n.nodeid)) into target_template;
                            end if;
                        end loop;    
                    end;
                    
                    return_label := trim(both from target_template);
                    if return_label = '' then
                        return 'Undefined';
                    end if;
                    return return_label;
                end;
                $$;

            create or replace function __arches_get_resourceinstance_list_label(resourceinstance_value jsonb, label_type text default 'name') returns text language plpgsql as $$
                declare
                    return_label     text := '';
                begin
                    if resourceinstance_value is null OR resourceinstance_value::text = 'null' then
                        return '';
                    end if;
                    
                    select string_agg(dvl.label, ', ')
                    from
                    (
                        select __arches_get_resourceinstance_label(dv.resource_instance, label_type) as label
                        from (
                            select jsonb_array_elements(resourceinstance_value) as resource_instance
                        ) dv
                    ) dvl
                    into return_label;
                    
                    return return_label;

                end;
                $$;

            create or replace function __arches_get_nodevalue_label(node_value jsonb, in_nodeid uuid) returns text language plpgsql as $$
                declare
                    return_label         text := '';
                    nodevalue_tileid     text;
                    value_nodeid         text;
                begin

                    if node_value is null or in_nodeid is null then
                        return '';
                    end if;

                    select n.config ->> 'nodeid'
                    into value_nodeid
                    from nodes n
                    where n.nodeid = in_nodeid::uuid;

                    select __arches_get_node_display_value(t.tiledata, value_nodeid)
                    into return_label
                    from tiles t
                    where t.tileid = node_value::uuid;
                    
                    if return_label is null then
                        return_label := '';
                    end if;
                    
                return return_label;
                end;
                $$;

            create or replace function __arches_get_node_display_value(in_tiledata jsonb, in_nodeid uuid) returns text language plpgsql as $$
                declare
                    display_value     text := '';
                    in_node_type     text;
                    in_node_config     json;
                begin
                    if in_nodeid is null or in_nodeid is null then
                        return '<invalid_nodeid>';
                    end if;
                    
                    if in_tiledata is null then
                        return '';
                    end if;

                    select n.datatype, n.config 
                    into in_node_type, in_node_config 
                    from nodes n where nodeid = in_nodeid::uuid;
                        
                    if in_node_type = 'semantic' then
                        return '<semantic>';
                    end if;
                    
                    if in_node_type is null then
                        return '';
                    end if;
                    
                    case in_node_type
                        when 'concept' then
                            display_value := __arches_get_concept_label((in_tiledata ->> in_nodeid::text)::uuid);
                        when 'concept-list' then
                            display_value := __arches_get_concept_list_label(in_tiledata -> in_nodeid::text);
                        when 'edtf' then
                            display_value := ((in_tiledata -> in_nodeid::text) ->> 'value');
                        when 'file-list' then
                            select string_agg(f.url,' | ') from (select (jsonb_array_elements(in_tiledata -> in_nodeid::text) -> 'name')::text as url) f into display_value;
                        when 'domain-value' then
                            display_value := __arches_get_domain_label((in_tiledata ->> in_nodeid::text)::uuid, in_nodeid);
                        when 'domain-value-list' then
                            display_value := __arches_get_domain_list_label(in_tiledata -> in_nodeid, in_nodeid);
                        when 'url' then
                            display_value := (in_tiledata -> in_nodeid::text ->> 'url');
                        when 'node-value' then
                            display_value := __arches_get_nodevalue_label(in_tiledata -> in_nodeid::text, in_nodeid);
                        when 'resource-instance' then
                            display_value := __arches_get_resourceinstance_label(in_tiledata -> in_nodeid::text, 'name');
                        when 'resource-instance-list' then
                            display_value := __arches_get_resourceinstance_list_label(in_tiledata -> in_nodeid::text, 'name');
                        else
                            -- print the content of the json
                            -- 'string'
                            -- 'number'
                            -- 'date' -----------------might need to look at date formatting?
                            -- 'boolean
                            -- 'geojson-feature-collection'
                            -- 'annotation'
                            -- 'any other custom datatype - will need a pattern to handle this'
                            display_value := (in_tiledata ->> in_nodeid::text)::text;
                        
                        end case;
                            
                    return display_value;
                end;
                $$;

            create or replace function __arches_accum_get_node_display_value(init text, in_tiledata jsonb, in_nodeid uuid) returns text language plpgsql as $$
                declare
                    display_name     text := '';
                    return_label     text := '';
                begin

                    select __arches_get_node_display_value(in_tiledata, in_nodeid)
                    into display_name;
                    
                    if display_name = '' then
                        return init;
                    end if;
                    
                    if init = '' then
                        return_label := display_name;
                    else
                        return_label := (init || ', ' || display_name);
                    end if;
                    
                    return return_label;
                end;
                $$;

            create or replace aggregate __arches_agg_get_node_display_value(in_tiledata jsonb, in_nodeid uuid)
                (
                    initcond = '',
                    stype = text,
                    sfunc = __arches_accum_get_node_display_value
                );

            create or replace function __arches_create_spatial_view_attribute_table(
                    spatial_view_name_slug text,
                    geometry_node_id uuid,
                    attribute_node_list jsonb,
                    schema_name text default 'public'
                ) returns text
                language plpgsql 
                strict
                as 
                $$
                declare
                    att_table_name     text;
                    tile_create         text := '';
                    node_create         text := '';
                    att_view_tbl         text;
                    att_comments         text := '';
                begin
                    att_table_name := format('%s.sp_attr_%s', schema_name, spatial_view_name_slug);
                    
                    att_comments = att_comments || format(
                                    'comment on column %s.%s is ''%s'';',
                                    att_table_name,
                                    'resourceinstanceid',
                                    'Globally unique Arches resource ID'
                                    );
                    
                    declare
                        tmp_nodegroupid_slug     text;
                        node_name_slug			text;
                        n                         record;
                    begin
                        for n in 
                                with attribute_nodes as (
                                    select * from jsonb_to_recordset(attribute_node_list) as x(nodeid uuid, description text)
                                )
                                select 
                                    n1.name, 
                                    n1.nodeid, 
                                    n1.nodegroupid,
                                    att_nodes.description
                                from nodes n1
                                    join (select * from attribute_nodes) att_nodes ON n1.nodeid = att_nodes.nodeid
                        loop
                            tmp_nodegroupid_slug := __arches_slugify(n.nodegroupid::text);
                            node_name_slug := __arches_slugify(n.name);
                            node_create = node_create || 
                                format('
                                    ,__arches_agg_get_node_display_value(distinct tile_%s.tiledata, ''%s'') as %s
                                    ',
                                        tmp_nodegroupid_slug,
                                        n.nodeid::text,
                                        node_name_slug
                                    );
                            
                            if tile_create not like (format('%%tile_%s%%',tmp_nodegroupid_slug)) then
                                tile_create = tile_create || 
                                    format(' 
                                    left outer join tiles tile_%s on r.resourceinstanceid = tile_%s.resourceinstanceid
                                        and tile_%s.nodegroupid = ''%s''
                                    ',
                                    tmp_nodegroupid_slug,
                                    tmp_nodegroupid_slug,
                                    tmp_nodegroupid_slug,
                                    n.nodegroupid::text);
                            end if;

                            if n.description is not null AND n.description <> '' then
                                att_comments = att_comments || format(
                                    'comment on column %s.%s is ''%s'';',
                                    att_table_name,
                                    node_name_slug,
                                    n.description
                                    );
                            end if;

                        end loop;
                    end;
                    
                    att_view_tbl := format(
                        '
                        create table %s 
                        tablespace pg_default
                        as
                        (
                            select 
                                r.resourceinstanceid::text as resourceinstanceid
                                %s
                            from resource_instances r
                                join geojson_geometries geo on geo.resourceinstanceid::text = r.resourceinstanceid::text
                                    and geo.nodeid = ''%s''
                                %s
                            group by
                                r.resourceinstanceid::text
                        )
                        with data;
                        
                        %s

                        create index on %s (resourceinstanceid);
                        
                        ',
                        att_table_name,
                        node_create, 
                        geometry_node_id, 
                        tile_create,
                        att_comments,
                        att_table_name);
                    
                    execute att_view_tbl;
                    
                    return att_table_name;
                end;
                $$;

            create or replace function __arches_delete_spatial_view_attribute_table(
                    spatial_view_name_slug text,
                    schema_name text default 'public'
                ) returns boolean
                language plpgsql 
                strict
                as 
                $$
                declare
                    success                 boolean := false;
                    sv_delete                 text := '';
                    att_table_name             text;
                begin
                    att_table_name := format('%s.sp_attr_%s', schema_name, spatial_view_name_slug);
                    sv_delete := format('
                            drop table if exists %s;
                            ',
                            att_table_name
                            );
                    
                    
                    execute sv_delete;
                    
                    success := true;
                    
                    return success;
                end;
                $$;

            create or replace function __arches_create_spatial_view(
                    spatial_view_name_slug      text,
                    geometry_node_id            uuid,
                    attribute_node_list         jsonb,
                    schema_name                 text default 'public',
                    spv_description             text default 'arches spatial view',
                    is_mixed_geometry_type      boolean default false
                ) returns boolean
                language plpgsql 
                strict
                as 
                $$
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
                    att_table_name := __arches_create_spatial_view_attribute_table(spatial_view_name_slug, geometry_node_id, attribute_node_list, schema_name);
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

                            grant select on table %s to arches_spatial_views;

                            comment on view %s is ''%s'';

                            ',
                            sv_name_slug_with_geom,
                            att_table_name,
                            geometry_node_id::text,
                            geom_type_filter,
                            sv_name_slug_with_geom,
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
                                    __arches_slugify(n1.name) as name, 
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
                                    n.name,
                                    n.description);
                            end loop;

                    end loop;
                    
                    execute sv_create;
                    
                    success := true;
                    
                    return success;
                end;
                $$;

            create or replace function __arches_update_spatial_view(
                    current_spatial_view_name_slug  text,
                    current_schema_name				text,
                    new_spatial_view_name_slug      text,
                    geometry_node_id        		uuid,
                    attribute_node_list     		jsonb,
                    new_schema_name             	text default 'public',
                    spv_description         		text default 'arches spatial view',
                    is_mixed_geometry_type  		boolean default false
                ) returns boolean
                language plpgsql 
                strict 
                as 
                $$
                declare
                    success     boolean := false;
                begin
                    success := __arches_delete_spatial_view(current_spatial_view_name_slug, current_schema_name);

                    if success = true then
                        success := __arches_create_spatial_view(new_spatial_view_name_slug, geometry_node_id, attribute_node_list, new_schema_name, spv_description, is_mixed_geometry_type);
                    end if;

                    return success;
                end;
                $$;

            create or replace function __arches_delete_spatial_view(
                    spatial_view_name_slug      text,
                    schema_name                 text default 'public'
                ) returns boolean
                language plpgsql 
                strict
                as 
                $$
                declare
                    sv_name_slug_with_geom      text;
                    success                     boolean := false;
                    sv_delete                   text := '';
                    att_table_name              text;
                    g                           record;
                    tmp_geom_type               text;
                begin
                    for g in select unnest(string_to_array('ST_Point,ST_LineString,ST_Polygon,mixed_geom'::text,',')) as geometry_type
                    loop
                        tmp_geom_type := g.geometry_type;
                        sv_name_slug_with_geom := format('%s.%s_%s',schema_name, spatial_view_name_slug, lower(replace(tmp_geom_type,'ST_','')));

                        sv_delete := sv_delete || 
                            format('
                            drop view if exists %s;
                            ',
                            sv_name_slug_with_geom
                            );
                    end loop;
                    
                    att_table_name := format('%s.sp_attr_%s', schema_name, spatial_view_name_slug);
                    sv_delete := sv_delete || 
                            format('
                            drop table if exists %s;
                            ',
                            att_table_name
                            );
                    
                    
                    execute sv_delete;
                    
                    success := true;
                    
                    return success;
                end;
                $$;

            create or replace function __arches_refresh_spatial_views()
                returns boolean
                language plpgsql
                as 
                $$
                declare
                    success boolean := false;
                    refresh_script text := '';
                    sv record;
                begin
                    for sv in select * from spatial_views where isactive = true
                    loop
                        refresh_script := refresh_script || format('select __arches_update_spatial_view(''%s'',''%s'',''%s'', ''%s''::uuid, ''%s''::jsonb, ''%s'', ''%s'', %L);'
                            , sv.slug
                            , sv.schema
                            , sv.slug
                            , sv.geometrynodeid
                            , sv.attributenodes
                            , sv.schema
                            , sv.description
                            , sv.ismixedgeometrytypes);

                    end loop;

                    if refresh_script <> '' then                     
                        execute refresh_script;
                    end if;

                    success := true;
                    
                    return success;
                end;
                $$;

            create or replace function __arches_trg_fnc_update_spatial_attributes()
                returns trigger 
                language plpgsql
                as $func$
                declare
                    trigger_tile            record;
                    spv                     record;
                begin
                    if tg_op = 'DELETE' then 
                        trigger_tile := old;
                    else
                        trigger_tile := new;
                    end if;

                    for spv in
                            select * from spatial_views where isactive = true
                    loop
                        declare
                            resource_geom_count     integer := 0;
                            found_attr_key_count    integer := 0;
                            insert_attr             text    := '';
                            delete_existing         text    := '';
                        begin
                            with attribute_nodes as (
                                select * from jsonb_to_recordset(spv.attributenodes) as x(nodeid uuid, description text)
                            )
                            select count(*) into found_attr_key_count 
                            from (select jsonb_object_keys(trigger_tile.tiledata) as node_id) keys
                            where keys.node_id::text in (select nodeid::text from attribute_nodes)
                                or keys.node_id::text = spv.geometrynodeid::text;

                            if found_attr_key_count < 1 then
                                continue; 
                            end if;
                            
                            declare
                                att_table_name          text := spv.schema || '.sp_attr_' || spv.slug;
                                tmp_nodegroupid_slug    text;
                                n                       record;
                                node_create             text := '';
                                tile_create             text := '';
                            begin

                                delete_existing := format('
                                    delete from %1$s where resourceinstanceid::uuid = %2$L::uuid;
                                    ',
                                    att_table_name,
                                    trigger_tile.resourceinstanceid
                                    );
                                execute delete_existing;

                                for n in 
                                        with attribute_nodes1 as (
                                            select * from jsonb_to_recordset(spv.attributenodes) as x(nodeid uuid, description text)
                                        )
                                        select 
                                            n1.name, 
                                            n1.nodeid, 
                                            n1.nodegroupid,
                                            att_nodes.description
                                        from nodes n1
                                            join (select * from attribute_nodes1) att_nodes ON n1.nodeid = att_nodes.nodeid
                                loop
                                    tmp_nodegroupid_slug := __arches_slugify(n.nodegroupid::text);
                                    node_create = node_create || 
                                        format(' ,__arches_agg_get_node_display_value(distinct tile_%s.tiledata, %L::uuid) as %s '
                                            ,tmp_nodegroupid_slug
                                            ,n.nodeid::text
                                            ,__arches_slugify(n.name)
                                        );
                                    
                                    if tile_create not like (format('%%tile_%s%%',tmp_nodegroupid_slug)) then
                                        tile_create = tile_create || 
                                            format(' left outer join tiles tile_%s on r.resourceinstanceid = tile_%s.resourceinstanceid
                                                and tile_%s.nodegroupid = ''%s''::uuid ',
                                            tmp_nodegroupid_slug,
                                            tmp_nodegroupid_slug,
                                            tmp_nodegroupid_slug,
                                            n.nodegroupid::text);
                                    end if;

                                end loop;

                                insert_attr := format(
                                    '
                                    insert into %s
                                        select 
                                            r.resourceinstanceid
                                            %s
                                        from resource_instances r
                                            join geojson_geometries geo on geo.resourceinstanceid = r.resourceinstanceid
                                                and geo.nodeid = %L
                                            %s
                                        group by
                                            r.resourceinstanceid
                                        having r.resourceinstanceid = %L::uuid
                                    ',
                                    att_table_name,
                                    node_create, 
                                    spv.geometrynodeid::text, 
                                    tile_create,
                                    trigger_tile.resourceinstanceid::text);

                            end;
                            execute insert_attr;

                        end;
                    end loop;

                    return trigger_tile;
                end;
                $func$;

            create constraint trigger __arches_trg_update_spatial_attributes
                after insert or update or delete
                on tiles
                deferrable initially deferred
                for each row
                    execute procedure __arches_trg_fnc_update_spatial_attributes();

            create or replace function __arches_trg_fnc_update_spatial_views()
                returns trigger 
                language plpgsql
                as $func$
                declare
                    sv_perform text := '';
                    valid_geom_nodeid boolean := false;
                    has_att_nodes integer := 0;
                    valid_att_nodeids boolean := false;
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
                                'select __arches_create_spatial_view(%L, %L::uuid, %L::jsonb, %L, %L, %L);'
                                , new.slug
                                , new.geometrynodeid
                                , new.attributenodes
                                , new.schema
                                , new.description
                                , new.ismixedgeometrytypes);
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
                                , new.ismixedgeometrytypes);
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
                $func$;

            create constraint trigger __arches_trg_update_spatial_views
                after insert or update or delete
                on spatial_views
                deferrable initially deferred
                for each row
                    execute procedure __arches_trg_fnc_update_spatial_views();

            select __arches_refresh_spatial_views();
        """

    reverse_sql_string = """
            DELETE FROM public.spatial_views;

            drop trigger __arches_trg_update_spatial_attributes on tiles;
            drop function if exists __arches_trg_fnc_update_spatial_attributes;

            drop trigger __arches_trg_update_spatial_views on spatial_views;
            drop function if exists __arches_trg_fnc_update_spatial_views;

            drop function if exists __arches_refresh_spatial_views;
            drop function if exists __arches_create_spatial_view;
            drop function if exists __arches_update_spatial_view;
            drop function if exists __arches_delete_spatial_view;
            drop function if exists __arches_create_spatial_view_attribute_table;
            drop function if exists __arches_delete_spatial_view_attribute_table;

            drop aggregate if exists __arches_agg_get_node_display_value(in_tiledata jsonb, in_nodeid uuid);
            drop function if exists __arches_accum_get_node_display_value;
            drop function if exists __arches_get_node_display_value;
            drop function if exists __arches_get_resourceinstance_list_label;
            drop function if exists __arches_get_domain_list_label;
            drop function if exists __arches_get_concept_label;
            drop function if exists __arches_get_domain_label;
            drop function if exists __arches_get_resourceinstance_label;
            drop function if exists __arches_get_nodevalue_label;

            do
            $do$
            declare
                database_name     text;
                sv_user_sql     text;
            begin
                if exists (
                    select from pg_catalog.pg_roles
                    where  rolname = 'arches_spatial_views') then

                    select current_database() into database_name;
                    
                    sv_user_sql := format('revoke connect on database %s from arches_spatial_views;', database_name);
                    execute sv_user_sql;

                end if;
            end
            $do$;

            drop role if exists arches_spatial_views;
        """

    operations = [
        migrations.RunSQL(sql_string, reverse_sql_string),
    ]
