CREATE OR REPLACE FUNCTION public.__arches_get_node_display_value(
    in_tiledata jsonb,
    in_nodeid uuid,
    language_id text DEFAULT 'en')
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

        if in_node_type in ('semantic', 'geojson-feature-collection', 'annotation') then
            return 'unsupported node type (' || in_node_type || ')';
        end if;

        if in_node_type is null then
            return '';
        end if;

        case in_node_type
            when 'string' then
                display_value := ((in_tiledata -> in_nodeid::text) -> language_id) ->> 'value';
            when 'concept' then
                display_value := __arches_get_concept_label((in_tiledata ->> in_nodeid::text)::uuid);
            when 'concept-list' then
                display_value := __arches_get_concept_list_label(in_tiledata -> in_nodeid::text);
            when 'edtf' then
                display_value := (in_tiledata ->> in_nodeid::text);
            when 'file-list' then
                display_value := __arches_get_file_list_label(in_tiledata -> in_nodeid::text, language_id);
            when 'domain-value' then
                display_value := __arches_get_domain_label((in_tiledata ->> in_nodeid::text)::uuid, in_nodeid, language_id);
            when 'domain-value-list' then
                display_value := __arches_get_domain_list_label(in_tiledata -> in_nodeid::text, in_nodeid, language_id);
            when 'url' then
                display_value := ((in_tiledata -> in_nodeid::text)::jsonb ->> 'url');
            when 'node-value' then
                display_value := __arches_get_nodevalue_label((in_tiledata -> in_nodeid::text)::uuid, in_nodeid, language_id);
            when 'resource-instance' then
                display_value := __arches_get_resourceinstance_label(in_tiledata -> in_nodeid::text, 'name', language_id);
            when 'resource-instance-list' then
                display_value := __arches_get_resourceinstance_list_label(in_tiledata -> in_nodeid::text, 'name', language_id);
            else
                display_value := (in_tiledata ->> in_nodeid::text)::text;

            end case;

        return display_value;
    end;
$BODY$;
