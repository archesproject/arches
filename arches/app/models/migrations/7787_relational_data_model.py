from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "7128_resource_instance_filter"),
    ]

    operations = [
        migrations.RunSQL(
            r"""
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
                    select regexp_replace("value", '[^a-z0-9\\\\-_]+', '_', 'gi') as "value"
                    from "removed_quotes"
                ),
                -- trims hyphens('-') if they exist on the head or tail of the string
                "trimmed" as (
                    select regexp_replace(regexp_replace("value", '\-+$', ''), '^\-', '') as "value"
                    from "separated"
                )
            select "value"
            from "trimmed";
            $$ language sql strict immutable;

            create or replace function __arches_get_node_value_sql(
                node public.nodes
            ) returns text as $$
            declare
                node_value_sql text;
                select_sql text = '(t.tiledata->>%L)';
                datatype text = 'text';
            begin
                select_sql = format(select_sql, node.nodeid);
                case node.datatype
                    when 'geojson-feature-collection' then
                        select_sql = format('
                            st_collect(
                                array(
                                    select st_transform(geom, 4326) from geojson_geometries
                                    where geojson_geometries.tileid = t.tileid and nodeid = %L
                                )
                            )',
                            node.nodeid
                        );
                        datatype = 'geometry';
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
                    when 'domain-value-list' then select_sql = format(
                        '(
                                        CASE
                                            WHEN t.tiledata->>%1$L is null THEN null
                                            ELSE ARRAY(
                                                SELECT jsonb_array_elements_text(
                                                    t.tiledata->%1$L
                                                )::uuid
                                            )
                                        END
                                    )',
                        node.nodeid
                    );
                    datatype = 'uuid[]';
                    when 'concept' then datatype = 'uuid';
                    when 'concept-list' then
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
                        datatype = 'uuid[]';
                    else
                        datatype = 'text';
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

            create or replace function __arches_tile_view_update() returns trigger as $$
                declare
                    view_namespace text;
                    group_id uuid;
                    graph_id uuid;
                    parent_id uuid;
                    tile_id uuid;
                    transaction_id uuid;
                    json_data json;
                    old_json_data jsonb;
                    edit_type text;
                begin
                    select graphid into graph_id from nodes where nodeid = group_id;
                    view_namespace = format('%s.%s', tg_table_schema, tg_table_name);
                    select obj_description(view_namespace::regclass, 'pg_class') into group_id;
                    if (TG_OP = 'DELETE') then
                        select tiledata into old_json_data from tiles where tileid = old.tileid;
                        delete from geojson_geometries where tileid = old.tileid;
                        delete from resource_x_resource where tileid = old.tileid;
                        delete from public.tiles where tileid = old.tileid;
                        insert into edit_log (
                            resourceclassid,
                            resourceinstanceid,
                            nodegroupid,
                            tileinstanceid,
                            edittype,
                            oldvalue,
                            timestamp,
                            note,
                            transactionid
                        ) values (
                            graph_id,
                            old.resourceinstanceid,
                            group_id,
                            old.tileid,
                            'tile delete',
                            old_json_data,
                            now(),
                            'loaded via SQL backend',
                            public.uuid_generate_v1mc()
                        );
                        return old;
                    else
                        select __arches_get_json_data_for_view(new, tg_table_schema, tg_table_name) into json_data;
                        select __arches_get_parent_id_for_view(new, tg_table_schema, tg_table_name) into parent_id;
                        tile_id = new.tileid;
                        if (new.transactionid is null) then
                            transaction_id = public.uuid_generate_v1mc();
                        else
                            transaction_id = new.transactionid;
                        end if;

                        if (TG_OP = 'UPDATE') then
                            select tiledata into old_json_data from tiles where tileid = tile_id;
                            edit_type = 'tile edit';
                            if (transaction_id = old.transactionid) then
                                transaction_id = public.uuid_generate_v1mc();
                            end if;
                            update public.tiles
                            set tiledata = json_data,
                                nodegroupid = group_id,
                                parenttileid = parent_id,
                                resourceinstanceid = new.resourceinstanceid
                            where tileid = new.tileid;
                        elsif (TG_OP = 'INSERT') then
                            old_json_data = null;
                            edit_type = 'tile create';
                            if tile_id is null then
                                tile_id = public.uuid_generate_v1mc();
                            end if;
                            insert into public.tiles(
                                tileid,
                                tiledata,
                                nodegroupid,
                                parenttileid,
                                resourceinstanceid
                            ) values (
                                tile_id,
                                json_data,
                                group_id,
                                parent_id,
                                new.resourceinstanceid
                            );
                        end if;
                        perform refresh_tile_geojson_geometries(tile_id);
                        perform __arches_refresh_tile_resource_relationships(tile_id);
                        insert into edit_log (
                            resourceclassid,
                            resourceinstanceid,
                            nodegroupid,
                            tileinstanceid,
                            edittype,
                            newvalue,
                            oldvalue,
                            timestamp,
                            note,
                            transactionid
                        ) values (
                            graph_id,
                            new.resourceinstanceid,
                            group_id,
                            tile_id,
                            edit_type,
                            json_data::jsonb,
                            old_json_data,
                            now(),
                            'loaded via SQL backend',
                            transaction_id
                        );
                        return new;
                    end if;
                end;
            $$ language plpgsql;

            create or replace function __arches_get_json_data_for_view(
                view_row anyelement,
                schema_name text,
                view_name text
            ) returns json as $$
            declare
                column_info record;
                query text;
                result jsonb;
                geom geometry;
                geometry_type text;
                geometry_query text;
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
                            'select st_geometrytype(
                                ($1::text::%s.%s).%s
                            )',
                            schema_name,
                            view_name,
                            column_info.column_name
                        );
                        execute query into geometry_type using view_row;
                        if geometry_type = 'ST_GeometryCollection' or geometry_type like 'ST_Multi%' then
                            geometry_query = E'from (
                                select st_asgeojson(
                                    st_dump(
                                        ($1::text::%s. %s).%s
                                    )
                                )::json->\\'geometry\\' as geom
                            ) as g';
                        else
                            geometry_query = 'from (
                                select st_asgeojson(
                                    ($1::text::%s. %s).%s
                                ) as geom
                            ) as g';
                        end if;
                        query = format(
                            E'select json_build_object(
                                    \\'type\\',
                                    \\'FeatureCollection\\',
                                    \\'features\\',
                                    json_agg(
                                        json_build_object(
                                            \\'type\\',
                                            \\'Feature\\',
                                            \\'geometry\\',
                                            g.geom::json,
                                            \\'properties\\',
                                            json_build_object()
                                        )
                                    )
                                )' || geometry_query,
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
                    if node_datatype in ('resource-instance-list', 'resource-instance') then
                        select jsonb_agg(
                            case
                                when e->>'resourceXresourceId' = '' then jsonb_set(
                                    e,
                                    '{resourceXresourceId}',
                                    to_jsonb(public.uuid_generate_v1mc())
                                )
                                else e
                            end
                        ) into result
                        from jsonb_array_elements(result) e(e);
                    end if;
                    tiledata = tiledata || jsonb_build_object(column_info.description, result);
                end loop;

                return tiledata::json;
            end
            $$ language plpgsql volatile;

            create or replace function __arches_get_parent_id_for_view(
                view_row anyelement,
                schema_name text,
                view_name text
            ) returns uuid as $$
            declare
                column_name text;
                query text;
                parent_id uuid;
                parent_column_count int;
            begin
                select a.attname into column_name
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
                    and d.description = 'parenttileid';

                get diagnostics parent_column_count = row_count;

                if parent_column_count > 0 then
                    query = format(
                        'select ($1::text::%s.%s).%s',
                        schema_name,
                        view_name,
                        column_name
                    );

                    execute query into parent_id using view_row;
                end if;

                return parent_id;
            end
            $$ language plpgsql volatile;

            create or replace function __arches_instance_view_update() returns trigger as $$
                declare
                    view_namespace text;
                    model_id uuid;
                    instance_id uuid;
                    transaction_id uuid;
                    edit_type text;
                begin
                    view_namespace = format('%s.%s', tg_table_schema, tg_table_name);
                    select obj_description(view_namespace::regclass, 'pg_class') into model_id;
                    if (TG_OP = 'DELETE') then
                        delete from public.resource_instances where resourceinstanceid = old.resourceinstanceid;
                        insert into edit_log (
                            resourceclassid,
                            resourceinstanceid,
                            edittype,
                            timestamp,
                            note,
                            transactionid
                        ) values (
                            model_id,
                            old.resourceinstanceid,
                            'delete',
                            now(),
                            'loaded via SQL backend',
                            public.uuid_generate_v1mc()
                        );
                        return old;
                    else
                        instance_id = new.resourceinstanceid;
                        if instance_id is null then
                            instance_id = public.uuid_generate_v1mc();
                        end if;

                        if (new.transactionid is null) then
                            transaction_id = public.uuid_generate_v1mc();
                        else
                            transaction_id = new.transactionid;
                        end if;

                        if (TG_OP = 'UPDATE') then
                            edit_type = 'edit';
                            if (transaction_id = old.transactionid) then
                                transaction_id = public.uuid_generate_v1mc();
                            end if;
                            update public.resource_instances
                            set createdtime = new.createdtime,
                                legacyid = new.legacyid
                            where resourceinstanceid = instance_id;
                        elsif (TG_OP = 'INSERT') then
                            edit_type = 'create';
                            insert into public.resource_instances(
                                resourceinstanceid,
                                graphid,
                                legacyid,
                                createdtime
                            ) values (
                                instance_id,
                                model_id,
                                new.legacyid,
                                now()
                            );
                        end if;
                        insert into edit_log (
                            resourceclassid,
                            resourceinstanceid,
                            edittype,
                            timestamp,
                            note,
                            transactionid
                        ) values (
                            model_id,
                            instance_id,
                            edit_type,
                            now(),
                            'loaded via SQL backend',
                            transaction_id
                        );
                        return new;
                    end if;
                end;
            $$ language plpgsql;

            create or replace function __arches_refresh_tile_resource_relationships(
                tile_id uuid
            ) returns boolean as $$
            declare
                resource_id uuid;
            begin
                select resourceinstanceid into resource_id from tiles where tileid = tile_id;

                delete from resource_x_resource where tileid = tile_id;

                with relationships as (
                    select n.nodeid,
                        jsonb_array_elements(t.tiledata->n.nodeid::text) as relationship
                    from tiles t
                        left join nodes n on t.nodegroupid = n.nodegroupid
                    where n.datatype in ('resource-instance-list', 'resource-instance')
                        and t.tileid = tile_id
                        and t.tiledata->>n.nodeid::text is not null
                )
                insert into resource_x_resource (
                    resourcexid,
                    notes,
                    relationshiptype,
                    resourceinstanceidfrom,
                    resourceinstanceidto,
                    inverserelationshiptype,
                    tileid,
                    nodeid,
                    created,
                    modified
                ) select
                    (relationship->>'resourceXresourceId')::uuid,
                    '',
                    relationship->>'ontologyProperty',
                    resource_id,
                    (relationship->>'resourceId')::uuid,
                    relationship->>'inverseOntologyProperty',
                    tile_id,
                    nodeid,
                    now(),
                    now()
                from relationships;

                return true;
            end;
            $$ language plpgsql;

            create or replace function __arches_get_labels_for_concept_node(
                node_id uuid,
                language_id text default 'en'
            ) returns table (
                depth int,
                valueid uuid,
                value text,
                conceptid uuid
            ) as $$
            declare
                collector_id uuid;
                value_id uuid;
            begin
                select (config->>'rdmCollection')::text into collector_id
                from nodes where nodeid = node_id;

                RETURN QUERY WITH RECURSIVE

                    ordered_relationships AS (
                    (
                        SELECT r.conceptidfrom, r.conceptidto, r.relationtype, (
                            SELECT v1.value
                            FROM values v1
                            WHERE v1.conceptid=r.conceptidto
                            AND v1.valuetype in ('prefLabel')
                            ORDER BY (
                                CASE WHEN v1.languageid = language_id THEN 10
                                WHEN v1.languageid like (language_id || '%') THEN 5
                                WHEN v1.languageid like (language_id || '%') THEN 2
                                ELSE 0
                                END
                            ) desc limit 1
                        ) as valuesto,
                        (
                            SELECT v2.value::int
                            FROM values v2
                            WHERE v2.conceptid=r.conceptidto
                            AND v2.valuetype in ('sortorder')
                            limit 1
                        ) as sortorder,
                        (
                            SELECT v3.value
                            FROM values v3
                            WHERE v3.conceptid=r.conceptidto
                            AND v3.valuetype in ('collector')
                            limit 1
                        ) as collector
                        FROM relations r
                        WHERE r.conceptidfrom = collector_id
                        and (r.relationtype = 'member')
                        ORDER BY sortorder, valuesto
                    )
                    UNION
                    (
                        SELECT r.conceptidfrom, r.conceptidto, r.relationtype,(
                            SELECT v4.value
                            FROM values v4
                            WHERE v4.conceptid=r.conceptidto
                            AND v4.valuetype in ('prefLabel')
                            ORDER BY (
                                CASE WHEN v4.languageid = language_id THEN 10
                                WHEN v4.languageid like (language_id || '%') THEN 5
                                WHEN v4.languageid like (language_id || '%') THEN 2
                                ELSE 0
                                END
                            ) desc limit 1
                        ) as valuesto,
                        (
                            SELECT v5.value::int
                            FROM values v5
                            WHERE v5.conceptid=r.conceptidto
                            AND v5.valuetype in ('sortorder')
                            limit 1
                        ) as sortorder,
                        (
                            SELECT v6.value
                            FROM values v6
                            WHERE v6.conceptid=r.conceptidto
                            AND v6.valuetype in ('collector')
                            limit 1
                        ) as collector
                        FROM relations r
                        JOIN ordered_relationships b ON(b.conceptidto = r.conceptidfrom)
                        WHERE (r.relationtype = 'member')
                        ORDER BY sortorder, valuesto
                    )
                ),

                children AS (
                    SELECT r.conceptidfrom, r.conceptidto,
                        to_char(row_number() OVER (), 'fm000000') as row,
                        r.collector,
                        1 AS depth       ---|NonRecursive Part
                        FROM ordered_relationships r
                        WHERE r.conceptidfrom = collector_id
                        and (r.relationtype = 'member')
                    UNION
                        SELECT r.conceptidfrom, r.conceptidto,
                        row || '-' || to_char(row_number() OVER (), 'fm000000'),
                        r.collector,
                        2 as depth      ---|RecursivePart
                        FROM ordered_relationships r
                        JOIN children b ON(b.conceptidto = r.conceptidfrom)
                        WHERE (r.relationtype = 'member')

                )

                select
                    c.depth,
                    v7.valueid,
                    v7.value,
                    v7.conceptid
                FROM children c
                join values v7 on v7.conceptid = c.conceptidto
                where v7.valuetype in ('prefLabel')
                    and v7.languageid like (language_id || '%')
                order by row;
            end $$ language plpgsql volatile;

            create or replace function __arches_get_node_id_for_view_column(
                schema_name text,
                view_name text,
                column_name text
            ) returns uuid as $$
            declare
                node_id uuid;
            begin

                select d.description::uuid into node_id
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
                    and a.attname = column_name;

                return node_id;
            end $$ language plpgsql volatile;

        """,
            """
            drop function if exists __arches_slugify cascade;
            drop function if exists __arches_get_node_value_sql cascade;
            drop function if exists __arches_create_nodegroup_view cascade;
            drop function if exists __arches_create_resource_model_views cascade;
            drop function if exists __arches_create_branch_views cascade;
            drop function if exists __arches_tile_view_update cascade;
            drop function if exists __arches_get_json_data_for_view cascade;
            drop function if exists __arches_get_parent_id_for_view cascade;
            drop function if exists __arches_instance_view_update cascade;
            drop function if exists __arches_refresh_tile_resource_relationships cascade;
            drop function if exists __arches_get_labels_for_concept_node cascade;
            drop function if exists __arches_get_node_id_for_view_column cascade;
        """,
        )
    ]
