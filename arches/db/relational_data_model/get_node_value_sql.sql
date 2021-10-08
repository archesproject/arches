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
