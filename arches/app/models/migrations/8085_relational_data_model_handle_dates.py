from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "7787_relational_data_model"),
    ]

    operations = [
        migrations.RunSQL(
            """
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
                    when 'date' then select_sql = format(
                        'to_date(
                            t.tiledata->>%L::text,
                            %L
                        )',
                        node.nodeid,
                        node.config->>'dateFormat'
                    );
                    datatype = 'timestamp';
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
                node public.nodes;
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
                    select n.* into node
                    from nodes n where n.nodeid = column_info.description::uuid;
                    if node.datatype = 'geojson-feature-collection' then
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
                    elsif node.datatype = 'date' then
                        query = format(
                            'select to_json(
                                to_char(
                                    ($1::text::%s.%s).%s,
                                    %L
                                )
                            )',
                            schema_name,
                            view_name,
                            column_info.column_name,
                            node.config->>'dateFormat'
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
                    if node.datatype in ('resource-instance-list', 'resource-instance') then
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
        """,
            """
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
        """,
        )
    ]
