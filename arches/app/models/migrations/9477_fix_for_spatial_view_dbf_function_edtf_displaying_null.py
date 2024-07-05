from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("models", "9477_fix_for_spatial_view_dbf_function_table_alias_error"),
    ]

    sql_string = """
            CREATE OR REPLACE FUNCTION public.__arches_get_node_display_value(
                in_tiledata jsonb,
                in_nodeid uuid)
                RETURNS text
                LANGUAGE 'plpgsql'
                COST 100
                VOLATILE PARALLEL UNSAFE
            AS $BODY$
                            declare
                                display_value   text := '';
                                in_node_type    text;
                                in_node_config  json;
                            begin
                                if in_nodeid is null or in_nodeid is null then
                                    return '<invalid_nodeid>';
                                end if;

                                if in_tiledata is null then
                                    return '';
                                end if;

                                select n.datatype, n.config
                                into in_node_type, in_node_config
                                from nodes n where nodeid = in_nodeid::uuid;

                                if in_node_type = 'semantic' then
                                    return '<semantic>';
                                end if;

                                if in_node_type is null then
                                    return '';
                                end if;

                                case in_node_type
                                    when 'concept' then
                                        display_value := __arches_get_concept_label((in_tiledata ->> in_nodeid::text)::uuid);
                                    when 'concept-list' then
                                        display_value := __arches_get_concept_list_label(in_tiledata -> in_nodeid::text);
                                    when 'edtf' then
                                        display_value := (in_tiledata ->> in_nodeid::text);
                                    when 'file-list' then
                                        select string_agg(f.url,' | ')
                                          from (select (jsonb_array_elements(in_tiledata -> in_nodeid::text) -> 'name')::text as url) f
                                          into display_value;
                                    when 'domain-value' then
                                        display_value := __arches_get_domain_label((in_tiledata ->> in_nodeid::text)::uuid, in_nodeid);
                                    when 'domain-value-list' then
                                        display_value := __arches_get_domain_list_label(in_tiledata -> in_nodeid, in_nodeid);
                                    when 'url' then
                                        display_value := (in_tiledata -> in_nodeid::text ->> 'url');
                                    when 'node-value' then
                                        display_value := __arches_get_nodevalue_label(in_tiledata -> in_nodeid::text, in_nodeid);
                                    when 'resource-instance' then
                                        display_value := __arches_get_resourceinstance_label(in_tiledata -> in_nodeid::text, 'name');
                                    when 'resource-instance-list' then
                                        display_value := __arches_get_resourceinstance_list_label(in_tiledata -> in_nodeid::text, 'name');
                                    else
                                        display_value := (in_tiledata ->> in_nodeid::text)::text;

                                    end case;

                                return display_value;
                            end;

            $BODY$;

            SELECT public.__arches_refresh_spatial_views();
        """

    reverse_sql_string = """
            create or replace function __arches_get_node_display_value(
                in_tiledata jsonb,
                in_nodeid uuid)
                returns text
                language plpgsql
            as $$
                declare
                    display_value   text := '';
                    in_node_type    text;
                    in_node_config  json;
                begin
                    if in_nodeid is null or in_nodeid is null then
                        return '<invalid_nodeid>';
                    end if;

                    if in_tiledata is null then
                        return '';
                    end if;

                    select n.datatype, n.config
                    into in_node_type, in_node_config
                    from nodes n where nodeid = in_nodeid::uuid;

                    if in_node_type = 'semantic' then
                        return '<semantic>';
                    end if;

                    if in_node_type is null then
                        return '';
                    end if;

                    case in_node_type
                        when 'concept' then
                            display_value := __arches_get_concept_label((in_tiledata ->> in_nodeid::text)::uuid);
                        when 'concept-list' then
                            display_value := __arches_get_concept_list_label(in_tiledata -> in_nodeid::text);
                        when 'edtf' then
                            display_value := ((in_tiledata -> in_nodeid::text) ->> 'value');
                        when 'file-list' then
                            select string_agg(f.url,' | ')
                              from (select (jsonb_array_elements(in_tiledata -> in_nodeid::text) -> 'name')::text as url) f
                              into display_value;
                        when 'domain-value' then
                            display_value := __arches_get_domain_label((in_tiledata ->> in_nodeid::text)::uuid, in_nodeid);
                        when 'domain-value-list' then
                            display_value := __arches_get_domain_list_label(in_tiledata -> in_nodeid, in_nodeid);
                        when 'url' then
                            display_value := (in_tiledata -> in_nodeid::text ->> 'url');
                        when 'node-value' then
                            display_value := __arches_get_nodevalue_label(in_tiledata -> in_nodeid::text, in_nodeid);
                        when 'resource-instance' then
                            display_value := __arches_get_resourceinstance_label(in_tiledata -> in_nodeid::text, 'name');
                        when 'resource-instance-list' then
                            display_value := __arches_get_resourceinstance_list_label(in_tiledata -> in_nodeid::text, 'name');
                        else
                            display_value := (in_tiledata ->> in_nodeid::text)::text;

                        end case;

                    return display_value;
                end;
            $$;
            SELECT public.__arches_refresh_spatial_views();
        """

    operations = [
        migrations.RunSQL(sql_string, reverse_sql_string),
    ]
