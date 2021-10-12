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
        if node_datatype = 'geojson-feature-collection' then
            query = format(
                E'select json_build_object(
                        \'type\',
                        \'FeatureCollection\',
                        \'features\',
                        json_agg(
                            json_build_object(
                                \'type\',
                                \'Feature\',
                                \'geometry\',
                                g.geom,
                                \'properties\',
                                json_build_object()
                            )
                        )
                    )
                from (
                    select json_array_elements(
                        (
                            st_asgeojson(
                                ($1::text::%s. %s).%s
                            )::jsonb ->> \'geometries\'
                        )::json
                    ) as geom
                ) as g',
                schema_name,
                view_name,
                column_info.column_name
            );
        else
            query = format(
                'select to_json(
                    ($1::text::%s.%s).%s
                )',
                schema_name,
                view_name,
                column_info.column_name
            );
        end if;
        execute query into result using view_row;
        tiledata = tiledata || jsonb_build_object(column_info.description, result);
    end loop;

    return tiledata::json;
end
$$ language plpgsql volatile;
