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
