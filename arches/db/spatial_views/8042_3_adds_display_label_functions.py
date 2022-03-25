from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ("models", "8042_2_spatialview_model"),
    ]

    sql_string = """
            create or replace function __arches_get_concept_label(concept_value uuid) returns text language plpgsql as $$
                declare
                    concept_label     text := '';
                begin
                    if concept_array is null then
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

    """

    reverse_sql_string = """
        drop aggregate if exists __arches_agg_get_node_display_value(in_tiledata jsonb, in_nodeid text);
        drop function if exists __arches_accum_get_node_display_value;
        drop function if exists __arches_get_node_display_value;
        drop function if exists __arches_get_resourceinstance_list_label;
        drop function if exists __arches_get_domain_list_label;
        drop function if exists __arches_get_concept_label;
        drop function if exists __arches_get_domain_label;
        drop function if exists __arches_get_resourceinstance_label;
        drop function if exists __arches_get_nodevalue_label;
    """

    operations = [
        migrations.RunSQL(sql_string, reverse_sql_string),
    ]