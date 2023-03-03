from django.db import migrations, models


# Add sensible defaults to the creation of resource model views.
class Migration(migrations.Migration):

    dependencies = [
        ("models", "9147_get_tile_cardinality_violations_i18n"),
    ]

    operations = [
        migrations.RunSQL(
            """
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
                    when 'string' then datatype = 'jsonb';
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
        )
    ]
