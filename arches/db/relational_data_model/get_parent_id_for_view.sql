create or replace function __arches_get_parent_id_for_view(
    view_row record,
    schema_name text,
    view_name text
) returns uuid as $$
declare
    column_name text;
    query text;
    parent_id uuid;
    parent_column_count int;
begin
    select a.attname into column_name
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
        and d.description = 'parenttileid';

    get diagnostics parent_column_count = row_count;

    if parent_column_count > 0 then
        query = format(
            'select ($1::text::%s.%s).%s',
            schema_name,
            view_name,
            column_name
        );

        execute query into parent_id using view_row;
    end if;

    return parent_id;
end
$$ language plpgsql volatile;
