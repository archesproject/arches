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
        select __arches_slugify(name) into schema_name
        from graphs where graphid = model_id;
    end if;

    creation_sql = format(
        'drop schema if exists %1$s cascade;
        create schema %1$s;
        create or replace view %1$s.instances as
            select r.*, e1.transactionid
            from resource_instances r
                left outer join edit_log e1 on (
                    r.resourceinstanceid = e1.resourceinstanceid::uuid
                    and e1.tileinstanceid is null
                )
                left outer join edit_log e2 on (
                    r.resourceinstanceid = e2.resourceinstanceid::uuid
                    and e2.tileinstanceid is null
                    and e1.timestamp < e2.timestamp
                )
            where e2.editlogid is null
            and r.graphid = %2$L;
        comment on view %1$s.instances is %2$L;
        create trigger %1$s_insert
            instead of insert or update or delete on %1$s.instances
            for each row
            execute function __arches_instance_view_update();
        ',
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
