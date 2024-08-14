from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("models", "9585_map_layer_public_flag"),
    ]

    sql_string = """
            CREATE OR REPLACE FUNCTION public.__arches_create_spatial_view_attribute_table(
                spatial_view_name_slug  text,
                geometry_node_id        uuid,
                attribute_node_list     jsonb,
                schema_name             text DEFAULT 'public'::text)
                RETURNS text
                LANGUAGE 'plpgsql'
                COST 100
                VOLATILE STRICT PARALLEL UNSAFE
            AS $BODY$
                declare
                    att_table_name  text;
                    tile_create     text := '';
                    node_create     text := '';
                    att_view_tbl    text;
                    att_comments    text := '';
                begin
                    att_table_name := format('%s.sp_attr_%s', schema_name, spatial_view_name_slug);

                    att_comments = att_comments || format(
                                    'comment on column %s.%s is ''%s'';',
                                    att_table_name,
                                    'resourceinstanceid',
                                    'Globally unique Arches resource ID'
                                    );

                    declare
                        tmp_nodegroupid_slug  text;
                        node_name_slug        text;
                        n                     record;
                    begin
                        for n in
                                with attribute_nodes as (
                                    select * from jsonb_to_recordset(attribute_node_list) as x(nodeid uuid, description text)
                                )
                                select
                                    n1.name,
                                    n1.nodeid,
                                    n1.nodegroupid,
                                    att_nodes.description
                                from nodes n1
                                    join (select * from attribute_nodes) att_nodes ON n1.nodeid = att_nodes.nodeid
                        loop
                            tmp_nodegroupid_slug := __arches_slugify(n.nodegroupid::text);
                            node_name_slug := __arches_slugify(n.name);
                            node_create = node_create ||
                                format('
                                    ,__arches_agg_get_node_display_value(distinct "tile_%s".tiledata, ''%s'') as %s
                                    ',
                                        tmp_nodegroupid_slug,
                                        n.nodeid::text,
                                        node_name_slug
                                    );

                            if tile_create not like (format('%%tile_%s%%',tmp_nodegroupid_slug)) then
                                tile_create = tile_create ||
                                    format('
                                    left outer join tiles "tile_%s" on r.resourceinstanceid = "tile_%s".resourceinstanceid
                                        and "tile_%s".nodegroupid = ''%s''
                                    ',
                                    tmp_nodegroupid_slug,
                                    tmp_nodegroupid_slug,
                                    tmp_nodegroupid_slug,
                                    n.nodegroupid::text);
                            end if;

                            if n.description is not null AND n.description <> '' then
                                att_comments = att_comments || format(
                                    'comment on column %s.%s is ''%s'';',
                                    att_table_name,
                                    node_name_slug,
                                    n.description
                                    );
                            end if;

                        end loop;
                    end;

                    att_view_tbl := format(
                        '
                        create table %s
                        tablespace pg_default
                        as
                        (
                            select
                                r.resourceinstanceid::text as resourceinstanceid
                                %s
                            from resource_instances r
                                join geojson_geometries geo on geo.resourceinstanceid::text = r.resourceinstanceid::text
                                    and geo.nodeid = ''%s''
                                %s
                            group by
                                r.resourceinstanceid::text
                        )
                        with data;

                        %s

                        create index on %s (resourceinstanceid);

                        ',
                        att_table_name,
                        node_create,
                        geometry_node_id,
                        tile_create,
                        att_comments,
                        att_table_name);

                    execute att_view_tbl;

                    return att_table_name;
                end;

            $BODY$;

            CREATE OR REPLACE FUNCTION public.__arches_trg_fnc_update_spatial_attributes()
                RETURNS trigger
                LANGUAGE 'plpgsql'
                COST 100
                VOLATILE NOT LEAKPROOF
            AS $BODY$
                declare
                    trigger_tile  record;
                    spv           record;
                begin
                    if tg_op = 'DELETE' then
                        trigger_tile := old;
                    else
                        trigger_tile := new;
                    end if;

                    for spv in
                            select * from spatial_views where isactive = true
                    loop
                        declare
                            resource_geom_count   integer := 0;
                            found_attr_key_count  integer := 0;
                            insert_attr           text    := '';
                            delete_existing       text    := '';
                        begin
                            with attribute_nodes as (
                                select * from jsonb_to_recordset(spv.attributenodes) as x(nodeid uuid, description text)
                            )
                            select count(*) into found_attr_key_count
                            from (select jsonb_object_keys(trigger_tile.tiledata) as node_id) keys
                            where keys.node_id::text in (select nodeid::text from attribute_nodes)
                                or keys.node_id::text = spv.geometrynodeid::text;

                            if found_attr_key_count < 1 then
                                continue;
                            end if;

                            declare
                                att_table_name        text := spv.schema || '.sp_attr_' || spv.slug;
                                tmp_nodegroupid_slug  text;
                                n                     record;
                                node_create           text := '';
                                tile_create           text := '';
                            begin

                                delete_existing := format('
                                    delete from %1$s where resourceinstanceid::uuid = %2$L::uuid;
                                    ',
                                    att_table_name,
                                    trigger_tile.resourceinstanceid
                                    );
                                execute delete_existing;

                                for n in
                                        with attribute_nodes1 as (
                                            select * from jsonb_to_recordset(spv.attributenodes) as x(nodeid uuid, description text)
                                        )
                                        select
                                            n1.name,
                                            n1.nodeid,
                                            n1.nodegroupid,
                                            att_nodes.description
                                        from nodes n1
                                            join (select * from attribute_nodes1) att_nodes ON n1.nodeid = att_nodes.nodeid
                                loop
                                    tmp_nodegroupid_slug := __arches_slugify(n.nodegroupid::text);
                                    node_create = node_create ||
                                        format(' ,__arches_agg_get_node_display_value(distinct "tile_%s".tiledata, %L::uuid) as %s '
                                            ,tmp_nodegroupid_slug
                                            ,n.nodeid::text
                                            ,__arches_slugify(n.name)
                                        );

                                    if tile_create not like (format('%%tile_%s%%',tmp_nodegroupid_slug)) then
                                        tile_create = tile_create ||
                                            format(' left outer join tiles "tile_%s" on r.resourceinstanceid = "tile_%s".resourceinstanceid
                                                and "tile_%s".nodegroupid = ''%s''::uuid ',
                                            tmp_nodegroupid_slug,
                                            tmp_nodegroupid_slug,
                                            tmp_nodegroupid_slug,
                                            n.nodegroupid::text);
                                    end if;

                                end loop;

                                insert_attr := format(
                                    '
                                    insert into %s
                                        select
                                            r.resourceinstanceid
                                            %s
                                        from resource_instances r
                                            join geojson_geometries geo on geo.resourceinstanceid = r.resourceinstanceid
                                                and geo.nodeid = %L
                                            %s
                                        group by
                                            r.resourceinstanceid
                                        having r.resourceinstanceid = %L::uuid
                                    ',
                                    att_table_name,
                                    node_create,
                                    spv.geometrynodeid::text,
                                    tile_create,
                                    trigger_tile.resourceinstanceid::text);

                            end;
                            execute insert_attr;

                        end;
                    end loop;

                    return trigger_tile;
                end;

            $BODY$;
        """

    reverse_sql_string = """
            create or replace function __arches_create_spatial_view_attribute_table(
                    spatial_view_name_slug  text,
                    geometry_node_id        uuid,
                    attribute_node_list     jsonb,
                    schema_name             text default 'public'
                ) returns text
                language plpgsql
                strict
                as
                $$
                declare
                    att_table_name  text;
                    tile_create     text := '';
                    node_create     text := '';
                    att_view_tbl    text;
                    att_comments    text := '';
                begin
                    att_table_name := format('%s.sp_attr_%s', schema_name, spatial_view_name_slug);

                    att_comments = att_comments || format(
                                    'comment on column %s.%s is ''%s'';',
                                    att_table_name,
                                    'resourceinstanceid',
                                    'Globally unique Arches resource ID'
                                    );

                    declare
                        tmp_nodegroupid_slug  text;
                        node_name_slug	      text;
                        n                     record;
                    begin
                        for n in
                                with attribute_nodes as (
                                    select * from jsonb_to_recordset(attribute_node_list) as x(nodeid uuid, description text)
                                )
                                select
                                    n1.name,
                                    n1.nodeid,
                                    n1.nodegroupid,
                                    att_nodes.description
                                from nodes n1
                                    join (select * from attribute_nodes) att_nodes ON n1.nodeid = att_nodes.nodeid
                        loop
                            tmp_nodegroupid_slug := __arches_slugify(n.nodegroupid::text);
                            node_name_slug := __arches_slugify(n.name);
                            node_create = node_create ||
                                format('
                                    ,__arches_agg_get_node_display_value(distinct tile_%s.tiledata, ''%s'') as %s
                                    ',
                                        tmp_nodegroupid_slug,
                                        n.nodeid::text,
                                        node_name_slug
                                    );

                            if tile_create not like (format('%%tile_%s%%',tmp_nodegroupid_slug)) then
                                tile_create = tile_create ||
                                    format('
                                    left outer join tiles tile_%s on r.resourceinstanceid = tile_%s.resourceinstanceid
                                        and tile_%s.nodegroupid = ''%s''
                                    ',
                                    tmp_nodegroupid_slug,
                                    tmp_nodegroupid_slug,
                                    tmp_nodegroupid_slug,
                                    n.nodegroupid::text);
                            end if;

                            if n.description is not null AND n.description <> '' then
                                att_comments = att_comments || format(
                                    'comment on column %s.%s is ''%s'';',
                                    att_table_name,
                                    node_name_slug,
                                    n.description
                                    );
                            end if;

                        end loop;
                    end;

                    att_view_tbl := format(
                        '
                        create table %s
                        tablespace pg_default
                        as
                        (
                            select
                                r.resourceinstanceid::text as resourceinstanceid
                                %s
                            from resource_instances r
                                join geojson_geometries geo on geo.resourceinstanceid::text = r.resourceinstanceid::text
                                    and geo.nodeid = ''%s''
                                %s
                            group by
                                r.resourceinstanceid::text
                        )
                        with data;

                        %s

                        create index on %s (resourceinstanceid);

                        ',
                        att_table_name,
                        node_create,
                        geometry_node_id,
                        tile_create,
                        att_comments,
                        att_table_name);

                    execute att_view_tbl;

                    return att_table_name;
                end;
                $$;

            create or replace function __arches_trg_fnc_update_spatial_attributes()
                returns trigger
                language plpgsql
                as $func$
                declare
                    trigger_tile  record;
                    spv           record;
                begin
                    if tg_op = 'DELETE' then
                        trigger_tile := old;
                    else
                        trigger_tile := new;
                    end if;

                    for spv in
                            select * from spatial_views where isactive = true
                    loop
                        declare
                            resource_geom_count   integer := 0;
                            found_attr_key_count  integer := 0;
                            insert_attr           text    := '';
                            delete_existing       text    := '';
                        begin
                            with attribute_nodes as (
                                select * from jsonb_to_recordset(spv.attributenodes) as x(nodeid uuid, description text)
                            )
                            select count(*) into found_attr_key_count
                            from (select jsonb_object_keys(trigger_tile.tiledata) as node_id) keys
                            where keys.node_id::text in (select nodeid::text from attribute_nodes)
                                or keys.node_id::text = spv.geometrynodeid::text;

                            if found_attr_key_count < 1 then
                                continue;
                            end if;

                            declare
                                att_table_name        text := spv.schema || '.sp_attr_' || spv.slug;
                                tmp_nodegroupid_slug  text;
                                n                     record;
                                node_create           text := '';
                                tile_create           text := '';
                            begin

                                delete_existing := format('
                                    delete from %1$s where resourceinstanceid::uuid = %2$L::uuid;
                                    ',
                                    att_table_name,
                                    trigger_tile.resourceinstanceid
                                    );
                                execute delete_existing;

                                for n in
                                        with attribute_nodes1 as (
                                            select * from jsonb_to_recordset(spv.attributenodes) as x(nodeid uuid, description text)
                                        )
                                        select
                                            n1.name,
                                            n1.nodeid,
                                            n1.nodegroupid,
                                            att_nodes.description
                                        from nodes n1
                                            join (select * from attribute_nodes1) att_nodes ON n1.nodeid = att_nodes.nodeid
                                loop
                                    tmp_nodegroupid_slug := __arches_slugify(n.nodegroupid::text);
                                    node_create = node_create ||
                                        format(' ,__arches_agg_get_node_display_value(distinct tile_%s.tiledata, %L::uuid) as %s '
                                            ,tmp_nodegroupid_slug
                                            ,n.nodeid::text
                                            ,__arches_slugify(n.name)
                                        );

                                    if tile_create not like (format('%%tile_%s%%',tmp_nodegroupid_slug)) then
                                        tile_create = tile_create ||
                                            format(' left outer join tiles tile_%s on r.resourceinstanceid = tile_%s.resourceinstanceid
                                                and tile_%s.nodegroupid = ''%s''::uuid ',
                                            tmp_nodegroupid_slug,
                                            tmp_nodegroupid_slug,
                                            tmp_nodegroupid_slug,
                                            n.nodegroupid::text);
                                    end if;

                                end loop;

                                insert_attr := format(
                                    '
                                    insert into %s

                                        select
                                            r.resourceinstanceid
                                            %s
                                        from resource_instances r
                                            join geojson_geometries geo on geo.resourceinstanceid = r.resourceinstanceid
                                                and geo.nodeid = %L
                                            %s
                                        group by
                                            r.resourceinstanceid
                                        having r.resourceinstanceid = %L::uuid
                                    ',
                                    att_table_name,
                                    node_create,
                                    spv.geometrynodeid::text,
                                    tile_create,
                                    trigger_tile.resourceinstanceid::text);

                            end;
                            execute insert_attr;

                        end;
                    end loop;

                    return trigger_tile;
                end;
                $func$;
        """

    operations = [
        migrations.RunSQL(sql_string, reverse_sql_string),
    ]
