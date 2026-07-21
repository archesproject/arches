import django_migrate_sql.operations
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("models", "12779_add_multicard_resource_descriptor"),
    ]

    operations = [
        django_migrate_sql.operations.CreateSQL(
            name="__arches_get_node_value_sql",
            sql="\ncreate or replace function __arches_get_node_value_sql(node nodes) returns text as\n$$\ndeclare\n    node_value_sql text;\n    select_sql text = '(t.tiledata->>%L)';\n    datatype text = 'text';\nbegin\n    select_sql = format(select_sql, node.nodeid);\n    if (node.config->>'pgDatatype' is not null) then\n        datatype = node.config->>'pgDatatype';\n    else\n        case node.datatype\n            when 'geojson-feature-collection' then datatype = 'geometry';\n            when 'string' then datatype = 'jsonb';\n            when 'number' then datatype = 'numeric';\n            when 'boolean' then datatype = 'boolean';\n            when 'resource-instance' then datatype = 'jsonb';\n            when 'resource-instance-list' then datatype = 'jsonb';\n            when 'annotation' then datatype = 'jsonb';\n            when 'file-list' then datatype = 'jsonb';\n            when 'url' then datatype = 'jsonb';\n            when 'date' then datatype = 'timestamp';\n            when 'node-value' then datatype = 'uuid';\n            when 'domain-value' then datatype = 'uuid';\n            when 'domain-value-list' then datatype = 'uuid[]';\n            when 'concept' then datatype = 'uuid';\n            when 'concept-list' then datatype = 'uuid[]';\n            else\n                datatype = 'text';\n            end case;\n        end if;\n        case datatype\n            when 'geometry' then\n                 select_sql = format('\n                    st_collect(\n                        array(\n                            select st_transform(geom, 4326) from geojson_geometries\n                            where geojson_geometries.tileid = t.tileid and nodeid = %L\n                        )\n                    )',\n                    node.nodeid\n                );\n            when 'timestamp' then\n                select_sql = format(\n                    'to_date(\n                        t.tiledata->>%L::text,\n                        %L\n                    )',\n                    node.nodeid,\n                    node.config->>'dateFormat'\n                );\n            when 'uuid[]' then\n                select_sql = format('(\n                        CASE\n                            WHEN t.tiledata->>%1$L is null THEN null\n                            ELSE ARRAY(\n                                SELECT jsonb_array_elements_text(\n                                    t.tiledata->%1$L\n                                )::uuid\n                            )\n                        END\n                    )', node.nodeid\n                );\n            else\n                null;\n            end case;\n\n\n        node_value_sql = format(\n            '%s::%s as \"%s\"',\n            select_sql,\n            datatype,\n            node.alias\n        );\n    return node_value_sql;\nend\n$$ language plpgsql volatile;\n",
            reverse_sql="""
create or replace function __arches_get_node_value_sql(node nodes) returns text as
$$
declare
    node_value_sql text;
    select_sql text = '(t.tiledata->>%L)';
    datatype text = 'text';
begin
    select_sql = format(select_sql, node.nodeid);
    if (node.config->>'pgDatatype' is not null) then
        datatype = node.config->>'pgDatatype';
    else
        case node.datatype
            when 'geojson-feature-collection' then datatype = 'geometry';
            when 'string' then datatype = 'jsonb';
            when 'number' then datatype = 'numeric';
            when 'boolean' then datatype = 'boolean';
            when 'resource-instance' then datatype = 'jsonb';
            when 'resource-instance-list' then datatype = 'jsonb';
            when 'annotation' then datatype = 'jsonb';
            when 'file-list' then datatype = 'jsonb';
            when 'url' then datatype = 'jsonb';
            when 'date' then datatype = 'timestamp';
            when 'node-value' then datatype = 'uuid';
            when 'domain-value' then datatype = 'uuid';
            when 'domain-value-list' then datatype = 'uuid[]';
            when 'concept' then datatype = 'uuid';
            when 'concept-list' then datatype = 'uuid[]';
            else
                datatype = 'text';
            end case;
        end if;
        case datatype
            when 'geometry' then
                 select_sql = format('
                    st_collect(
                        array(
                            select st_transform(geom, 4326) from geojson_geometries
                            where geojson_geometries.tileid = t.tileid and nodeid = %L
                        )
                    )',
                    node.nodeid
                );
            when 'timestamp' then
                select_sql = format(
                    'to_date(
                        t.tiledata->>%L::text,
                        %L
                    )',
                    node.nodeid,
                    node.config->>'dateFormat'
                );
            when 'uuid[]' then
                select_sql = format('(
                        CASE
                            WHEN t.tiledata->>%1$L is null THEN null
                            ELSE ARRAY(
                                SELECT jsonb_array_elements_text(
                                    t.tiledata->%1$L
                                )::uuid
                            )
                        END
                    )', node.nodeid
                );
            else
                null;
            end case;


        node_value_sql = format(
            '%s::%s as "%s"',
            select_sql,
            datatype,
            __arches_slugify(node.name)
        );
    return node_value_sql;
end
$$ language plpgsql volatile;
""",
        ),
        django_migrate_sql.operations.CreateSQL(
            name="__arches_slugify",
            sql='\ncreate extension if not exists "unaccent";\n\ncreate or replace function __arches_slugify(\n    "value" text\n) returns text as $$\n    -- removes accents (diacritic signs) from a given string\n    with "unaccented" as (\n        select unaccent("value") as "value"\n    ),\n    -- lowercases the string\n    "lowercase" as (\n        select lower("value") as "value"\n        from "unaccented"\n    ),\n    -- remove single and double quotes\n    "removed_quotes" as (\n        select regexp_replace("value", \'[\'\'"]+\', \'\', \'gi\') as "value"\n        from "lowercase"\n    ),\n    -- replaces anything that\'s not a letter, number, or underscore(\'_\') with an underscore(\'_\')\n    "separated" as (\n        select regexp_replace("value", \'[^a-z0-9_]+\', \'_\', \'gi\') as "value"\n        from "removed_quotes"\n    ),\n    -- trims underscores(\'_\') if they exist on the head or tail of the string\n    "trimmed" as (\n        select regexp_replace(regexp_replace("value", \'_+$\', \'\'), \'^_\', \'\') as "value"\n        from "separated"\n    )\nselect "value"\nfrom "trimmed";\n$$ language sql strict immutable;\n',
            reverse_sql="""
create extension if not exists "unaccent";

create or replace function __arches_slugify(
    "value" text
) returns text as $$
    -- removes accents (diacritic signs) from a given string
    with "unaccented" as (
        select unaccent("value") as "value"
    ),
    -- lowercases the string
    "lowercase" as (
        select lower("value") as "value"
        from "unaccented"
    ),
    -- remove single and double quotes
    "removed_quotes" as (
        select regexp_replace("value", '[''"]+', '', 'gi') as "value"
        from "lowercase"
    ),
    -- replaces anything that's not a letter, number, hyphen('-'), or underscore('_') with an underscore('_')
    "separated" as (
        select regexp_replace("value", '[^a-z0-9_-]+', '_', 'gi') as "value"
        from "removed_quotes"
    ),
    -- trims hyphens('-') if they exist on the head or tail of the string
    "trimmed" as (
        select regexp_replace(regexp_replace("value", '-+$', ''), '^-', '') as "value"
        from "separated"
    )
select "value"
from "trimmed";
$$ language sql strict immutable;
""",
        ),
        django_migrate_sql.operations.CreateSQL(
            name="__arches_create_nodegroup_view",
            sql='\ncreate or replace function __arches_create_nodegroup_view(\n    group_id uuid,\n    view_name text default null,\n    schema_name text default \'public\',\n    parent_name text default \'parenttileid\'\n) returns text as $$\ndeclare\n    creation_sql text;\n    additional_sql text;\n    node public.nodes;\n    parent_group_id uuid;\nbegin\n    if view_name is null then\n        select alias into view_name\n        from nodes where nodeid = group_id;\n    end if;\n\n    creation_sql = format(\n        \'drop view if exists "%1$s"."%2$s";\n        create or replace view "%1$s"."%2$s" as\n            select t.tileid,\n        \',\n        schema_name,\n        view_name\n    );\n\n    additional_sql = format(\'\n        comment on view "%1$s"."%2$s" is %3$L;\n        create trigger %2$s_insert\n            instead of insert or update or delete on "%1$s"."%2$s"\n            for each row\n            execute function __arches_tile_view_update();\n        \',\n        schema_name,\n        view_name,\n        group_id\n    );\n\n    for node in select n.*, d.*\n        from nodes n\n            join d_data_types d on d.datatype = n.datatype\n        where nodegroupid = group_id\n            and d.defaultwidget is not null\n    loop\n        creation_sql = creation_sql || format(\'\n            %s,\',\n            __arches_get_node_value_sql(node)\n        );\n\n        additional_sql = additional_sql || format(\'\n                comment on column "%s"."%s"."%s" is %L;\n            \',\n            schema_name,\n            view_name,\n            node.alias,\n            node.nodeid\n        );\n    end loop;\n\n    select parentnodegroupid into parent_group_id\n    from node_groups where nodegroupid = group_id;\n\n    if parent_group_id is not null then\n        creation_sql = creation_sql || format(\'\n            t.parenttileid as "%s",\n        \', parent_name);\n        additional_sql = additional_sql || format(\'\n            comment on column "%1$s"."%2$s"."%3$s" is %4$L;\n            \',\n            schema_name,\n            view_name,\n            parent_name,\n            \'parenttileid\'\n        );\n    end if;\n\n    creation_sql = creation_sql || format(\'\n            t.resourceinstanceid,\n            t.nodegroupid,\n            e1.transactionid\n        from tiles t\n        left outer join edit_log e1 on (t.tileid = e1.tileinstanceid::uuid)\n        left outer join edit_log e2 on (\n            t.tileid = e2.tileinstanceid::uuid\n            and e1.timestamp < e2.timestamp\n        )\n        where t.nodegroupid = %L\n        and e2.editlogid is null;\',\n        group_id\n    );\n\n    execute creation_sql;\n    execute additional_sql;\n    return format(\'view "%s.%s" created.\', schema_name, view_name);\nend\n$$ language plpgsql volatile;\n',
            reverse_sql="""
create or replace function __arches_create_nodegroup_view(
    group_id uuid,
    view_name text default null,
    schema_name text default 'public',
    parent_name text default 'parenttileid'
) returns text as $$
declare
    creation_sql text;
    additional_sql text;
    node public.nodes;
    parent_group_id uuid;
begin
    if view_name is null then
        select __arches_slugify(name) into view_name
        from nodes where nodeid = group_id;
    end if;

    creation_sql = format(
        'drop view if exists "%1$s"."%2$s";
        create or replace view "%1$s"."%2$s" as
            select t.tileid,
        ',
        schema_name,
        view_name
    );

    additional_sql = format('
        comment on view "%1$s"."%2$s" is %3$L;
        create trigger %2$s_insert
            instead of insert or update or delete on "%1$s"."%2$s"
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
                comment on column "%s"."%s"."%s" is %L;
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
            t.parenttileid as "%s",
        ', parent_name);
        additional_sql = additional_sql || format('
            comment on column "%1$s"."%2$s"."%3$s" is %4$L;
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
""",
            dependencies=[("models", "__arches_get_node_value_sql")],
        ),
        django_migrate_sql.operations.CreateSQL(
            name="__arches_create_branch_views",
            sql="\ncreate or replace function __arches_create_branch_views(\n    group_id uuid,\n    schema_name text default 'public',\n    parent_name text default ''\n) returns text as $$\ndeclare\n    view_name text;\n    node record;\nbegin\n    -- create view using __arches_create_nodegroup_view\n    select alias into view_name\n    from nodes\n    where nodeid = group_id;\n\n    perform __arches_create_nodegroup_view(\n        group_id,\n        view_name,\n        schema_name,\n        parent_name\n    );\n\n    -- recursively call __arches_create_branch_views for all child groups\n    for node in select *\n        from node_groups\n        where parentnodegroupid = group_id\n    loop\n        perform __arches_create_branch_views(node.nodegroupid, schema_name, view_name);\n    end loop;\n\n    return format('views created for branch.');\nend\n$$ language plpgsql volatile;\n",
            reverse_sql="""
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
""",
            dependencies=[("models", "__arches_create_nodegroup_view")],
        ),
        django_migrate_sql.operations.CreateSQL(
            name="__arches_create_resource_model_views",
            sql='\ncreate or replace function __arches_create_resource_model_views(\n    model_id uuid,\n    schema_name text default null\n) returns text as $$\ndeclare\n    creation_sql text;\n    node record;\nbegin\n    -- create schema and instance view for model\n    if schema_name is null then\n        select __arches_slugify(name->>\'en\') into schema_name\n        from graphs where graphid = model_id;\n    end if;\n\n    creation_sql = format(\n        \'drop schema if exists "%1$s" cascade;\n        create schema "%1$s";\n        create or replace view "%1$s".instances as\n            select r.*, e1.transactionid\n            from resource_instances r\n                left outer join edit_log e1 on (\n                    r.resourceinstanceid = e1.resourceinstanceid::uuid\n                    and e1.tileinstanceid is null\n                )\n                left outer join edit_log e2 on (\n                    r.resourceinstanceid = e2.resourceinstanceid::uuid\n                    and e2.tileinstanceid is null\n                    and e1.timestamp < e2.timestamp\n                )\n            where e2.editlogid is null\n            and r.graphid = %2$L;\n        comment on view "%1$s".instances is %2$L;\n        create trigger %1$s_insert\n            instead of insert or update or delete on "%1$s".instances\n            for each row\n            execute function __arches_instance_view_update();\n        \',\n        schema_name,\n        model_id\n    );\n    execute creation_sql;\n\n    -- iterate over top nodes and create views for each branch\n    for node in select *\n        from nodes n\n        join node_groups g on g.nodegroupid = n.nodegroupid\n        where n.nodeid = n.nodegroupid\n        and g.parentnodegroupid is null\n        and graphid = model_id\n    loop\n        perform __arches_create_branch_views(node.nodeid, schema_name, \'\');\n    end loop;\n\n    return format(\'schema "%s" created for resource model.\', schema_name);\nend\n$$ language plpgsql volatile;\n',
            reverse_sql="""
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
        select __arches_slugify(name->>'en') into schema_name
        from graphs where graphid = model_id;
    end if;

    creation_sql = format(
        'drop schema if exists "%1$s" cascade;
        create schema "%1$s";
        create or replace view "%1$s".instances as
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
        comment on view "%1$s".instances is %2$L;
        create trigger %1$s_insert
            instead of insert or update or delete on "%1$s".instances
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
""",
            dependencies=[
                ("models", "__arches_create_branch_views"),
                ("models", "__arches_slugify"),
            ],
        ),
    ]
