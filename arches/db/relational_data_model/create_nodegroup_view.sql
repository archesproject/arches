create or replace function __arches_create_nodegroup_view(
    group_id uuid,
    view_name text default null,
    schema_name text default 'public',
    parent_name text default 'parenttileid'
) returns text as $$
declare
    creation_sql text;
    node record;
    parent_group_id uuid;
begin
    if view_name is null then
        select __arches_slugify(name) into view_name
        from nodes where nodeid = group_id;
    end if;

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
        where nodegroupid = group_id
            and d.defaultwidget is not null
    loop
        creation_sql = creation_sql || __arches_get_node_value_sql(node);
    end loop;

    select parentnodegroupid into parent_group_id
    from node_groups where nodegroupid = group_id;

    if parent_group_id is not null then
        creation_sql = creation_sql || format('
            parenttileid as %s,
        ', parent_name);
    end if;

    creation_sql = creation_sql || format('
            resourceinstanceid
        from tiles
        where nodegroupid = %L;',
        group_id
    );

    execute creation_sql;
    return format('view "%s.%s" created.', schema_name, view_name);
end
$$ language plpgsql volatile;
