create or replace function __arches_get_json_data_for_view(
    view_row record,
    schema_name text,
    view_name text
) returns json as $$
declare
    tiledata json = '{}'::json;
begin
    -- iterate over columns in view and inspect comment
    -- if it is not "parenttileid", assume it is a data column and handle
    -- for each get node datatype and then transform to json value
    -- and assign value to json using node id
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
        and d.description != 'parenttileid';
    loop
        -- get node data type and set tiledata property...
    end loop;

    return tiledata;
end
$$ language plpgsql volatile;
