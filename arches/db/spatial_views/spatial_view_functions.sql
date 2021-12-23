/* --------------- DROP ALL ---------------
drop function if exists __arches_create_spatial_view;
drop function if exists __arches_update_spatial_view;
drop function if exists __arches_delete_spatial_view;
drop function if exists __arches_create_attribute_view;
drop aggregate if exists __arches_agg_get_node_display_value(in_tiledata jsonb, in_nodeid text);
drop function if exists __arches_accum_get_node_display_value;
drop function if exists __arches_get_node_display_value;
drop function if exists __arches_get_resourceinstance_list_label;
drop function if exists __arches_get_domain_list_label;
drop function if exists __arches_get_concept_label;
drop function if exists __arches_get_domain_label;
drop function if exists __arches_get_resourceinstance_label;
drop function if exists __arches_get_nodevalue_label;
drop function if exists __arches_slugify;
drop role if exists arches_featureservices;
*/

----------- existing from ROB

create or replace function __arches_slugify(
	"value" text
) returns text as $$
	-- removes accents (diacritic signs) from a given string
	--with "unaccented" as (
	--	select unaccent("value") as "value"
	--),
	-- lowercases the string
	with "lowercase" as (
		select lower("value") as "value"
		--from "unaccented"
	),
	-- remove single and double quotes
	"removed_quotes" as (
		select regexp_replace("value", '[''"]+', '', 'gi') as "value"
		from "lowercase"
	),
	-- replaces anything that's not a letter, number, hyphen('-'), or underscore('_') with an underscore('_')
	"separated" as (
		select regexp_replace("value", '[^a-z0-9\\\\-_]+', '_', 'gi') as "value"
		from "removed_quotes"
	),
	-- trims hyphens('-') if they exist on the head or tail of the string
	"trimmed" as (
		select regexp_replace(regexp_replace("value", '\-+$', ''), '^\-', '') as "value"
		from "separated"
	)
select "value"
from "trimmed";
$$ language sql strict immutable;
------------------------------

-- ROLE

do
$do$
begin
	if not exists (
		select from pg_catalog.pg_roles
		where  rolname = 'arches_featureservices') then

		create role arches_featureservices with
		login
		nosuperuser
		inherit
		nocreatedb
		nocreaterole
		noreplication
		--encrypted password 'md5967438f66634c78452443a93cc7293a4';
		password 'arches_featureservices';

		grant connect on database aher to arches_featureservices;
	end if;
end
$do$;

-- FUNCTIONS

create or replace function __arches_get_concept_label(concept_value text) returns text language plpgsql as $$
declare
	concept_label text := '';
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
	concept_list text;
begin

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
	in_node_config jsonb;
	return_label text;
begin
 	if domain_value is null or domain_value = '' or in_nodeid = '' then
		return '';
	end if;	

	select n.config
	into in_node_config
	from nodes n
	where n.nodeid = in_nodeid::uuid;

	select opt.text
		into return_label
	from jsonb_populate_recordset(in_node_config -> 'options') opts
	where opts.text = domain_value;
	
	if return_label is null then
		return_label = '';
	end if;
	
return return_label;
end;
$$;

--drop function if exists __arches_get_domain_list_label;
create or replace function __arches_get_domain_list_label(domain_value_list jsonb, nodeid text) returns text language plpgsql as $$
declare
	return_label text := '';
begin
 	if domain_value_list is null or in_nodeid = '' then
		return '';
	end if;
	
	select string_agg(dvl.label, ', ')
	from
	(
		select __arches_get_domain_label(dv.domain_value) as label
		from (
			select jsonb_array_elements_text(domain_value_list::json) as domain_value
		) dv
	 ) dvl
	into return_label;
	
return return_label;
end;
$$;

create or replace function __arches_get_resourceinstance_label(resourceinstance_value jsonb, label_type text default 'name') returns text language plpgsql as $$
declare
	return_label text := '';
	
	target_resourceinstanceid uuid;
	target_graph_funct_config jsonb;
	target_graphid uuid;
	target_nodegroupid uuid;
	target_template text;
	target_tiledata jsonb;
	target_provisionaledits jsonb;
	target_data jsonb;
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
		tiledata_keycount integer := 0;
		provisionaledits_users_keycount integer := 0;
		provisionaledits_userid text;
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
	return_label text := '';
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
	return_label text := '';
	nodevalue_tileid text;
	value_nodeid text;
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
	display_value text := '';
	in_node_type text;
	in_node_config json;
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
			display_value := __arches_get_domain_label(in_tiledata -> in_nodeid, in_nodeid);
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
	display_name text := '';
	return_label text := '';
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


create or replace function __arches_create_attribute_view(
	spatial_view_name_slug text,
	geometry_node_id uuid,
	attribute_node_list text
) returns text
language plpgsql 
strict
as 
$$
declare
	att_view_name 	text;
	tile_create 	text := '';
	node_create 	text := '';
	att_view 		text;
	
begin
	att_view_name := format('attr_%s', spatial_view_name_slug);
	raise notice 'att_view_name: %', att_view_name;
	attribute_node_list = replace(attribute_node_list,' ','');

	declare
		tmp_nodegroupid_slug text;
		n record;
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
		create materialized view %s 
		tablespace pg_default
		as
		(
			select 
				r.resourceinstanceid
				%s
			from resource_instances r
				join geojson_geometries geo on geo.resourceinstanceid = r.resourceinstanceid
					and geo.nodeid = ''%s''
				%s
			group by
				r.resourceinstanceid
		)
		with data;
		
		create unique index on %s (resourceinstanceid);
		
		',
		att_view_name,
		node_create, 
		geometry_node_id, 
		tile_create,
		att_view_name);
	
	execute att_view;
	
	return att_view_name;
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
	sv_name_slug text;
	sv_name_slug_with_geom text;
	success boolean := false;
	sv_create text := '';
	att_view_name text;
	g record;
	tmp_geom_type text;
begin
	sv_name_slug := __arches_slugify(spatial_view_name);
	att_view_name := __arches_create_attribute_view(sv_name_slug, geometry_node_id, attribute_node_list);

	for g in select unnest(string_to_array('ST_Point,ST_LineString,ST_Polygon'::text,',')) as geometry_type
	loop
		if att_view_name <> 'error' then
		
			tmp_geom_type := g.geometry_type;
			sv_name_slug_with_geom := format('%s_%s',sv_name_slug, lower(replace(tmp_geom_type,'ST_','')));
			
			sv_create := sv_create || 
				format('
				create or replace view %s AS
				select 
					geo.id AS gid,
					geo.tileid, 
					geo.nodeid,
					geo.geom, att.*
					FROM geojson_geometries geo
						join %s att ON geo.resourceinstanceid = att.resourceinstanceid
				where geo.nodeid = ''%s''
					and ST_GeometryType(geo.geom) = ''%s'';

				GRANT SELECT ON TABLE %s TO arches_featureservices;

				',
				sv_name_slug_with_geom,
				att_view_name,
				geometry_node_id::text,
				tmp_geom_type,
				sv_name_slug_with_geom);
		end if;
		
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
	success boolean := false;
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
	sv_name_slug text;
	sv_name_slug_with_geom text;
	success boolean := false;
	sv_delete text := '';
	att_view_name text;
	g record;
	tmp_geom_type text;
begin
	-- slugify the main view name
	sv_name_slug := __arches_slugify(spatial_view_name);
	
	for g in select unnest(string_to_array('ST_Point,ST_LineString,ST_Polygon'::text,',')) as geometry_type
	loop
		tmp_geom_type := g.geometry_type;
		sv_name_slug_with_geom := format('%s_%s',sv_name_slug, lower(replace(tmp_geom_type,'ST_','')));

		sv_delete := sv_delete || 
			format('
			drop view if exists %s cascade;
			',
			sv_name_slug_with_geom
			);
	end loop;
	
	att_view_name := format('attr_%s', sv_name_slug);
	sv_delete := sv_delete || 
			format('
			drop materialized view if exists %s;
			',
			att_view_name
			);
	
	
	execute sv_delete;
	
	success := true;
	
	return success;
end;
$$;