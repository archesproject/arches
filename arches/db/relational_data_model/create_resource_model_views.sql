create or replace function __arches_create_resource_model_views(
    model_id uuid,
    schema_name text default null
) returns text as $$
declare
    creation_sql text;
    node record;
begin
    -- create schema and instance view for model
    if schema_name is null then
        select name into schema_name
        from graphs where graphid = model_id;
    end if;

    creation_sql = format(
        'drop schema if exists %1$s cascade;
        create schema %1$s;
        create or replace view %1$s.instances as
            select * from resource_instances
            where graphid = %2$L;',
        schema_name,
        model_id
    );
    execute creation_sql;

    -- iterate over top nodes and create views for each branch
    for node in select *
        from nodes n
        join node_groups g on g.nodegroupid = n.nodegroupid
        where n.nodeid = n.nodegroupid
        and g.parentnodegroupid is null
        and graphid = model_id
    loop
        perform __arches_create_branch_views(node.nodeid, schema_name, '');
    end loop;

    return format('schema "%s" created for resource model.', schema_name);
end
$$ language plpgsql volatile;
