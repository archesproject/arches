create or replace function __arches_create_branch_views(
    group_id uuid,
    schema_name text default 'public',
    parent_name text default ''
) returns text as $$
declare
    view_name text;
    node record;
begin
    -- create view using __arches_create_nodegroup_view
    select __arches_slugify(name) into view_name
    from nodes
    where nodeid = group_id;

    perform __arches_create_nodegroup_view(
        group_id,
        view_name,
        schema_name,
        parent_name
    );

    -- recursively call __arches_create_branch_views for all child groups
    for node in select *
        from node_groups
        where parentnodegroupid = group_id
    loop
        perform __arches_create_branch_views(node.nodegroupid, schema_name, view_name);
    end loop;

    return format('views created for branch.');
end
$$ language plpgsql volatile;
