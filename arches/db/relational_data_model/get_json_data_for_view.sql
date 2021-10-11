create or replace function __arches_get_json_data_for_view(
    view_row record,
    schema_name text,
    view_name text
) returns json as $$
declare
    column_info record;
    query text;
    result jsonb;
    geom geometry;
    node_datatype text;
    tiledata jsonb = '{}'::jsonb;
begin
    for column_info in select a.attname as column_name,
        d.description
    from pg_class as c
        inner join pg_attribute as a on c.oid = a.attrelid
        left join pg_namespace n on n.oid = c.relnamespace
        left join pg_tablespace t on t.oid = c.reltablespace
        left join pg_description as d on (
            d.objoid = c.oid
            and d.objsubid = a.attnum
        )
    where c.relkind in('r', 'v')
        and n.nspname = schema_name
        and c.relname = view_name
        and d.description is not null
        and d.description != 'parenttileid'
    loop
        select datatype into node_datatype
        from nodes where nodeid = column_info.description::uuid;
        query = format(
            'select ($1::text::%s.%s).%s',
            schema_name,
            view_name,
            column_info.column_name
        );
        if view_name is null then
            execute query into geom using view_row;
            raise notice '%', st_astext(geom);
        -- else
        end if;
        execute query into result using view_row;
        tiledata = tiledata || jsonb_build_object(column_info.description, result);
    end loop;

    return tiledata::json;
end
$$ language plpgsql volatile;
