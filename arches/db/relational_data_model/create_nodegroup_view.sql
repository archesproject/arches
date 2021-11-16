create or replace function __arches_create_nodegroup_view(
    group_id uuid,
    view_name text default null,
    schema_name text default 'public',
    parent_name text default 'parenttileid'
) returns text as $$
declare
    creation_sql text;
    additional_sql text;
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
            select t.tileid,
        ',
        schema_name,
        view_name
    );

    additional_sql = format('
        comment on view %1$s.%2$s is %3$L;
        create trigger %2$s_insert
            instead of insert or update or delete on %1$s.%2$s
            for each row
            execute function __arches_tile_view_update();
        ',
        schema_name,
        view_name,
        group_id
    );

    for node in select n.*, d.*
        from nodes n
            join d_data_types d on d.datatype = n.datatype
        where nodegroupid = group_id
            and d.defaultwidget is not null
    loop
        creation_sql = creation_sql || format('
            %s,',
            __arches_get_node_value_sql(node)
        );

        additional_sql = additional_sql || format('
                comment on column %s.%s.%s is %L;
            ',
            schema_name,
            view_name,
            __arches_slugify(node.name),
            node.nodeid
        );
    end loop;

    select parentnodegroupid into parent_group_id
    from node_groups where nodegroupid = group_id;

    if parent_group_id is not null then
        creation_sql = creation_sql || format('
            t.parenttileid as %s,
        ', parent_name);
        additional_sql = additional_sql || format('
            comment on column %1$s.%2$s.%3$s is %4$L;
            ',
            schema_name,
            view_name,
            parent_name,
            'parenttileid'
        );
    end if;

    creation_sql = creation_sql || format('
            t.resourceinstanceid,
            t.nodegroupid,
            e1.transactionid
        from tiles t
        left outer join edit_log e1 on (t.tileid = e1.tileinstanceid::uuid)
        left outer join edit_log e2 on (
            t.tileid = e2.tileinstanceid::uuid
            and e1.timestamp < e2.timestamp
        )
        where t.nodegroupid = %L
        and e2.editlogid is null;',
        group_id
    );

    execute creation_sql;
    execute additional_sql;
    return format('view "%s.%s" created.', schema_name, view_name);
end
$$ language plpgsql volatile;
