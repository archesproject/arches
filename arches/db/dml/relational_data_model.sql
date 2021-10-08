create extension if not exists "unaccent";

drop function if exists __arches_slugify;
create or replace function __arches_slugify("value" text) returns text as $$ -- removes accents (diacritic signs) from a given string --
    with "unaccented" as (
        select unaccent("value") as "value"
    ),
    -- lowercases the string
    "lowercase" as (
        select lower("value") as "value"
        from "unaccented"
    ),
    -- remove single and double quotes
    "removed_quotes" as (
        select regexp_replace("value", '[''"]+', '', 'gi') as "value"
        from "lowercase"
    ),
    -- replaces anything that's not a letter, number, hyphen('-'), or underscore('_') with an underscore('_')
    "hyphenated" as (
        select regexp_replace("value", '[^a-z0-9\\-_]+', '_', 'gi') as "value"
        from "removed_quotes"
    ),
    -- trims hyphens('-') if they exist on the head or tail of the string
    "trimmed" as (
        select regexp_replace(regexp_replace("value", '\-+$', ''), '^\-', '') as "value"
        from "hyphenated"
    )
select "value"
from "trimmed";
$$ language sql strict immutable;

drop function if exists __arches_get_node_value_sql;
create or replace function __arches_get_node_value_sql(
    node record
) returns text as $$
declare
    node_value_sql text;
    select_sql text = '(tiledata->%L)';
    datatype text = 'text';
begin
    select_sql = format(select_sql, node.nodeid);
    case node.datatype
        when 'geojson-feature-collection' then
            select_sql = format('
                st_collect(
                    array(
                        select geom
                        from geojson_geometries
                        where tileid = tileid
                        and nodeid = %L
                    )
                )',
                node.nodeid
            );
            datatype = 'geometry';
        when 'number' then
            datatype = 'numeric';
        when 'concept' then
            datatype = 'uuid';
        when 'domain-value' then
            datatype = 'uuid';
        when 'date' then
            datatype = 'timestamp';
        when 'boolean' then
            datatype = 'boolean';
        end case;

        node_value_sql = format('
            %s::%s as %s,',
            select_sql,
            datatype,
            __arches_slugify(node.name)
        );
    return node_value_sql;
end
$$ language plpgsql volatile;

drop function if exists __arches_create_nodegroup_view;
create or replace function __arches_create_nodegroup_view(
    view_name text,
    schema_name text,
    group_id uuid
) returns text as $$
declare
    creation_sql text;
    node record;
begin
    creation_sql = format(
        'drop view if exists %1$s.%2$s;
        create or replace view %1$s.%2$s as
            select tileid,
        ',
        schema_name,
        view_name
    );

    for node in select n.*, d.*
        from nodes n
            join d_data_types d on d.datatype = n.datatype
        where nodegroupid = '6cd37abc-583f-11ea-b5fa-a683e74f7416'
            and d.defaultwidget is not null
    loop
        creation_sql = creation_sql || get_node_value_sql(node);
    end loop;

    creation_sql = creation_sql || format('
            resourceinstanceid,
            parenttileid
        from tiles
        where nodegroupid = %L;',
        group_id
    );

    execute creation_sql;
    return format('view "%s.%s" created.', schema_name, view_name);
end
$$ language plpgsql volatile;
