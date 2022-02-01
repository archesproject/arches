/* --------------- DROP ALL ---------------
drop function if exists __arches_create_spatial_view;
drop function if exists __arches_update_spatial_view;
drop function if exists __arches_delete_spatial_view;
drop function if exists __arches_create_spatial_view_attribute_table;
drop function if exists __arches_delete_spatial_view_attribute_table;
drop function if exists __arches_create_spatial_attribute_trigger_function;
drop function if exists __arches_delete_spatial_attribute_trigger_function;
drop function if exists __arches_create_spatial_attribute_trigger;
drop function if exists __arches_delete_spatial_attribute_trigger;
drop aggregate if exists __arches_agg_get_node_display_value(in_tiledata jsonb, in_nodeid text);
drop function if exists __arches_accum_get_node_display_value;
drop function if exists __arches_get_node_display_value;
drop function if exists __arches_get_resourceinstance_list_label;
drop function if exists __arches_get_domain_list_label;
drop function if exists __arches_get_concept_label;
drop function if exists __arches_get_domain_label;
drop function if exists __arches_get_resourceinstance_label;
drop function if exists __arches_get_nodevalue_label;
drop role if exists arches_featureservices;
*/

-- ROLE

do
$do$
declare
    database_name     text;
    fs_user_sql     text;
begin
    if not exists (
        select from pg_catalog.pg_roles
        where  rolname = 'arches_featureservices') then

        select current_database() into database_name;

        create role arches_featureservices with
        login
        nosuperuser
        inherit
        nocreatedb
        nocreaterole
        noreplication
        --encrypted password 'md5967438f66634c78452443a93cc7293a4';
        password 'arches_featureservices';

        fs_user_sql := format('grant connect on database %s to arches_featureservices;', database_name);
        execute fs_user_sql;

    end if;
end
$do$;

-- FUNCTIONS - DISPLAY VALUES

create or replace function __arches_get_concept_label(concept_value text) returns text language plpgsql as $$
declare
    concept_label     text := '';
begin
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
        select __arches_get_concept_label(x.conceptid) as label
        from (select json_array_elements_text(concept_array::json) as conceptid) x
     ) d
    into concept_list;
    
    if (concept_list is null) then
        concept_list := '';
    end if;
 
return concept_list;
end;
$$;

create or replace function __arches_get_domain_label(domain_value text, in_nodeid text) returns text language plpgsql as $$
declare
    in_node_config     jsonb;
    return_label     text;
begin
     if domain_value is null or in_nodeid = '' then
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


create or replace function __arches_get_domain_list_label(domain_value_list jsonb, in_nodeid text) returns text language plpgsql as $$
declare
    return_label     text := '';
begin
     if domain_value_list is null or in_nodeid = '' then
        return '';
    end if;
    
    select string_agg(dvl.label, ', ')
    from
    (
        select __arches_get_domain_label(dv.domain_value::text, in_nodeid) as label
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
        raise notice 'resourceinstance_value is null';
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
    
    select fxg.config
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
                select replace(target_template, format('<%s>',n.name), __arches_get_node_display_value(target_data, n.nodeid::text)) into target_template;
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

create or replace function __arches_get_nodevalue_label(node_value jsonb, in_nodeid text) returns text language plpgsql as $$
declare
    return_label         text := '';
    nodevalue_tileid     text;
    value_nodeid         text;
begin

    if node_value is null or in_nodeid is null or in_nodeid = '' then
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

create or replace function __arches_get_node_display_value(in_tiledata jsonb, in_nodeid text) returns text language plpgsql as $$
declare
    display_value     text := '';
    in_node_type     text;
    in_node_config     json;
begin
    if in_nodeid is null or in_nodeid = '' then
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
            display_value := __arches_get_concept_label(in_tiledata ->> in_nodeid);
        when 'concept-list' then
            display_value := __arches_get_concept_list_label(in_tiledata -> in_nodeid);
        when 'edtf' then
            display_value := ((in_tiledata -> in_nodeid) ->> 'value');
        when 'file-list' then
            select string_agg(f.url,' | ') from (select (jsonb_array_elements(in_tiledata -> in_nodeid) -> 'name')::text as url) f into display_value;
        when 'domain-value' then
            display_value := __arches_get_domain_label(in_tiledata ->> in_nodeid, in_nodeid);
        when 'domain-value-list' then
            display_value := __arches_get_domain_list_label(in_tiledata -> in_nodeid, in_nodeid);
        when 'url' then
            display_value := (in_tiledata -> in_nodeid ->> 'url');
        when 'node-value' then
            display_value := __arches_get_nodevalue_label(in_tiledata -> in_nodeid, in_nodeid);
        when 'resource-instance' then
            display_value := __arches_get_resourceinstance_label(in_tiledata -> in_nodeid, 'name');
        when 'resource-instance-list' then
            display_value := __arches_get_resourceinstance_list_label(in_tiledata -> in_nodeid, 'name');
        else
            -- print the content of the json
            -- 'string'
            -- 'number'
            -- 'date' -----------------might need to look at date formatting?
            -- 'boolean
            -- 'geojson-feature-collection'
            -- 'annotation'
            -- 'any other custom datatype - will need a pattern to handle this'
            display_value := (in_tiledata ->> in_nodeid)::text;
        
        end case;
            
    return display_value;
end;
$$;

create or replace function __arches_accum_get_node_display_value(init text, in_tiledata jsonb, in_nodeid text) returns text language plpgsql as $$
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

create or replace aggregate __arches_agg_get_node_display_value(in_tiledata jsonb, in_nodeid text)
(
    initcond = '',
    stype = text,
    sfunc = __arches_accum_get_node_display_value
);

-- FUNCTIONS - create spatial view trigger functions

create or replace function __arches_create_spatial_attribute_trigger_function(
    sp_view_name_slug text,
    sp_geometry_node_id uuid,
    sp_nodeids_list text
) returns boolean
language plpgsql 
strict
as 
$$
declare
    sp_attr_trigger_function text := '';
    success boolean := false;
begin
    sp_attr_trigger_function := format(
        '
        create or replace function __arches_trg_fnc_spatial_attributes_%1$s() -- sp_view_name_slug
        returns trigger 
        language plpgsql
        as $func$
        declare
            resource_geom_count     integer := 0;
            attr_nodeids            text    := replace(%2$L,'' '',''''); -- sp_nodeids_list;
            geometry_node_id        text    := %3$L; -- sp_geometry_node_id;
            found_attr_key_count    integer := 0;
            insert_attr             text    := '''';
            trigger_tile            record;
        begin
            -- set the working context depending on the operation
            if tg_op = ''DELETE'' then 
                trigger_tile := old;
            else
                trigger_tile := new;
            end if;

            -- checks to see if it needs regenerating--

            -- nodeid key check - are we working with a tile valid for this sp view?

            select count(*) into found_attr_key_count 
            from (select jsonb_object_keys(trigger_tile.tiledata) as node_id) keys
            where keys.node_id::text in (select unnest(string_to_array(attr_nodeids,'','')) as node_id)
                or keys.node_id::text = geometry_node_id;

            -- stop if tile has nothing to do with this view
            if found_attr_key_count < 1 then
                return trigger_tile; 
            end if;

            -- delete the existing rows for this resource
            delete from sp_attr_%1$s where resourceinstanceid = trigger_tile.resourceinstanceid;

            -- insert the new attrs
            
            declare
                att_table_name          text := ''sp_attr_%1$s'';
                attribute_node_list     text := attr_nodeids;
                tmp_nodegroupid_slug    text;
                n                       record;
                node_create             text := '''';
                tile_create             text := '''';
            begin
            
                for n in 
                        select 
                            name, 
                            nodeid, 
                            nodegroupid 
                        from nodes 
                        where nodeid::text in (select unnest(string_to_array(attribute_node_list,'','')) as nodeid)
                loop
                    tmp_nodegroupid_slug := __arches_slugify(n.nodegroupid::text);
                    node_create = node_create || 
                        format(
                            ''
                            ,__arches_agg_get_node_display_value(distinct tile_%%s.tiledata, %%L) as %%s
                            ''
                            ,tmp_nodegroupid_slug
                            ,n.nodeid::text
                            ,__arches_slugify(n.name)
                        );
                    
                    if tile_create not like (format(''%%%%tile_%%s%%%%'',tmp_nodegroupid_slug)) then
                        tile_create = tile_create || 
                            format('' 
                            left outer join tiles tile_%%s on r.resourceinstanceid = tile_%%s.resourceinstanceid
                                and tile_%%s.nodegroupid = ''''%%s''''
                            '',
                            tmp_nodegroupid_slug,
                            tmp_nodegroupid_slug,
                            tmp_nodegroupid_slug,
                            n.nodegroupid::text);
                    end if;

                end loop;

                -- pull together 
                insert_attr := format(
                    ''
                    insert into %%s
                        select 
                            r.resourceinstanceid
                            %%s
                        from resource_instances r
                            join geojson_geometries geo on geo.resourceinstanceid = r.resourceinstanceid
                                and geo.nodeid = %%L
                            %%s
                        group by
                            r.resourceinstanceid
                        having r.resourceinstanceid = %%L::uuid
                    '',
                    att_table_name,
                    node_create, 
                    geometry_node_id::text, 
                    tile_create,
                    trigger_tile.resourceinstanceid::text);

            end;
            
            execute insert_attr;

            -- end insert --

            return trigger_tile;
        end;
        $func$
        '
        ,sp_view_name_slug
        ,sp_nodeids_list
        ,sp_geometry_node_id
    );

    execute sp_attr_trigger_function;
    
    success := true;

    return success;
end;
$$;

create or replace function __arches_delete_spatial_attribute_trigger_function(
    sp_view_name_slug text
) returns boolean
language plpgsql 
strict
as 
$$
declare
    sp_attr_trigger_function text := '';
    success boolean := false;
begin
    sp_attr_trigger_function := format('drop function if exists __arches_trg_fnc_spatial_attributes_%1$s', sp_view_name_slug);
    execute sp_attr_trigger_function;
    success := true;
    return success;
end;
$$;

-- FUNCTIONS - create spatial view triggers

create or replace function __arches_create_spatial_attribute_trigger(
    sp_view_name_slug text,
    sp_geometry_node_id uuid,
    sp_nodeids_list text
) returns boolean
language plpgsql 
strict
as 
$$
declare
    sp_attr_trigger text := '';
    t_fnc_created boolean := false;
    success boolean := false;
begin
    -- create the trigger function
    select __arches_create_spatial_attribute_trigger_function(sp_view_name_slug, sp_geometry_node_id, sp_nodeids_list) into t_fnc_created;

    -- create the trigger
    sp_attr_trigger := format('
        create constraint trigger __arches_trg_spatial_attribute_%1$s
        after insert or update or delete
        on tiles
        deferrable initially deferred
        for each row
            execute procedure __arches_trg_fnc_spatial_attributes_%1$s()', sp_view_name_slug);
    
    execute sp_attr_trigger;

    success := true;

    return success;
end;
$$;

create or replace function __arches_delete_spatial_attribute_trigger(
    sp_view_name_slug text
) returns boolean
language plpgsql 
strict
as 
$$
declare
    del_sp_attr_trigger text := '';
    t_fnc_deleted boolean := false;
    success boolean := false;
begin
    del_sp_attr_trigger := format('drop trigger if exists __arches_trg_spatial_attribute_%1$s on tiles;', sp_view_name_slug);
    execute del_sp_attr_trigger;
    select __arches_delete_spatial_attribute_trigger_function(sp_view_name_slug) into t_fnc_deleted;
    success := true;

    return success;
end;
$$;


-- FUNCTIONS - create spatial views

create or replace function __arches_create_spatial_view_attribute_table(
    spatial_view_name_slug text,
    geometry_node_id uuid,
    attribute_node_list text
) returns text
language plpgsql 
strict
as 
$$
declare
    att_table_name     text;
    tile_create     text := '';
    node_create     text := '';
    att_view         text;
    
begin
    att_table_name := format('sp_attr_%s', spatial_view_name_slug);
    attribute_node_list = replace(attribute_node_list,' ','');

    declare
        tmp_nodegroupid_slug     text;
        n                         record;
    begin
    
        for n in 
                select 
                    name, 
                    nodeid, 
                    nodegroupid 
                from nodes 
                where nodeid::text IN (select unnest(string_to_array(attribute_node_list,',')) as nodeid)
        loop
            tmp_nodegroupid_slug := __arches_slugify(n.nodegroupid::text);
            node_create = node_create || 
                format('
                    ,__arches_agg_get_node_display_value(distinct tile_%s.tiledata, ''%s'') as %s
                    ',
                        tmp_nodegroupid_slug,
                        n.nodeid::text,
                        __arches_slugify(n.name));
            
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

        end loop;
    end;
    
    -- pull together 
    att_view := format(
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
        
        create unique index on %s (resourceinstanceid);
        
        ',
        att_table_name,
        node_create, 
        geometry_node_id, 
        tile_create,
        att_table_name);
    
    execute att_view;
    
    return att_table_name;
end;
$$;

create or replace function __arches_delete_spatial_view_attribute_table(
    spatial_view_name text
) returns boolean
language plpgsql 
strict
as 
$$
declare
    sv_name_slug             text;
    success                 boolean := false;
    sv_delete                 text := '';
    att_table_name             text;
begin
    sv_name_slug := __arches_slugify(spatial_view_name);
    att_table_name := format('sp_attr_%s', sv_name_slug);
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
    spatial_view_name text,
    geometry_node_id uuid,
    attribute_node_list text
) returns boolean
language plpgsql 
strict
as 
$$
declare
    sv_name_slug             text;
    sv_name_slug_with_geom     text;
    success                 boolean := false;
    sv_create                 text := '';
    att_table_name             text;
    g                         record;
    tmp_geom_type             text;
    trigger_success         boolean := false;
begin
    sv_name_slug := __arches_slugify(spatial_view_name);
    att_table_name := __arches_create_spatial_view_attribute_table(sv_name_slug, geometry_node_id, attribute_node_list);
    if att_table_name = 'error' then
        return success;
    end if;

    trigger_success := __arches_create_spatial_attribute_trigger(sv_name_slug, geometry_node_id, attribute_node_list);


    for g in select unnest(string_to_array('ST_Point,ST_LineString,ST_Polygon'::text,',')) as geometry_type
    loop
                
        tmp_geom_type := g.geometry_type;
        sv_name_slug_with_geom := format('%s_%s',sv_name_slug, lower(replace(tmp_geom_type,'ST_','')));
        
        sv_create := sv_create || 
            format('
            create or replace view %s AS
            select 
                geo.id AS gid,
                geo.tileid::text AS tileid, 
                geo.nodeid::text AS nodeid,
                geo.geom, att.*
                FROM geojson_geometries geo
                    join %s att ON geo.resourceinstanceid::text = att.resourceinstanceid::text
            where geo.nodeid = ''%s''
                and ST_GeometryType(geo.geom) = ''%s'';

            GRANT SELECT ON TABLE %s TO arches_featureservices;

            ',
            sv_name_slug_with_geom,
            att_table_name,
            geometry_node_id::text,
            tmp_geom_type,
            sv_name_slug_with_geom);
        
    end loop;
    execute sv_create;
    
    success := true;
    
    return success;
end;
$$;

create or replace function __arches_update_spatial_view(
    spatial_view_name text,
    geometry_node_id uuid,
    attribute_node_list text
) returns boolean
language plpgsql 
strict 
as 
$$
declare
    success     boolean := false;
begin
    success := __arches_delete_spatial_view(spatial_view_name);

    if success = true then
        success := __arches_create_spatial_view(spatial_view_name, geometry_node_id, attribute_node_list);
    end if;

    return success;
end;
$$;

create or replace function __arches_delete_spatial_view(
    spatial_view_name text
) returns boolean
language plpgsql 
strict
as 
$$
declare
    sv_name_slug             text;
    sv_name_slug_with_geom     text;
    success                 boolean := false;
    sv_delete                 text := '';
    att_table_name             text;
    g                         record;
    tmp_geom_type             text;
    trigger_success         boolean := false;
begin
    -- slugify the main view name
    sv_name_slug := __arches_slugify(spatial_view_name);
    trigger_success := __arches_delete_spatial_attribute_trigger(sv_name_slug);
    for g in select unnest(string_to_array('ST_Point,ST_LineString,ST_Polygon'::text,',')) as geometry_type
    loop
        tmp_geom_type := g.geometry_type;
        sv_name_slug_with_geom := format('%s_%s',sv_name_slug, lower(replace(tmp_geom_type,'ST_','')));

        sv_delete := sv_delete || 
            format('
            drop view if exists %s;
            ',
            sv_name_slug_with_geom
            );
    end loop;
    
    att_table_name := format('sp_attr_%s', sv_name_slug);
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