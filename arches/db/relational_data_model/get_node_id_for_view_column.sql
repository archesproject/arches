create or replace function __arches_get_node_id_for_view_column(
    schema_name text,
    view_name text,
    column_name text
) returns uuid as $$
declare
    node_id uuid;
begin

    select d.description::uuid into node_id
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
        and a.attname = column_name;

    return node_id;
end $$ language plpgsql volatile;
