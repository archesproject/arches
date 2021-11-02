create or replace function __arches_get_node_value_sql(
    node record
) returns text as $$
declare
    node_value_sql text;
    select_sql text = '(tiledata->>%L)';
    datatype text = 'text';
begin
    select_sql = format(select_sql, node.nodeid);
    case node.datatype
        when 'geojson-feature-collection' then
            select_sql = format('
                st_collect(
                    array(
                        select st_transform(geom, 4326) from geojson_geometries
                        where geojson_geometries.tileid = tiles.tileid and nodeid = %L
                    )
                )',
                node.nodeid
            );
            datatype = 'geometry';
        when 'number' then datatype = 'numeric';
        when 'boolean' then datatype = 'boolean';
        when 'concept-list' then
            select_sql = format('(
                    CASE
                        WHEN tiles.tiledata->>%1$L is null THEN null
                        ELSE ARRAY(
                            SELECT jsonb_array_elements_text(
                                    tiles.tiledata->%1$L
                                ) AS jsonb_array_elements_text
                        )
                    END
                )', node.nodeid
            );
            datatype = 'text[]';
        else
            datatype = 'text';
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
