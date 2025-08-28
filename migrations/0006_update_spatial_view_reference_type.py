from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("arches_controlled_lists", "0005_add_reference_select_widget_mapping"),
    ]

    forward_sql = """
        CREATE OR REPLACE FUNCTION __arches_get_preferred_label(
            item_id UUID,
            language_id TEXT DEFAULT 'en'
        )
        RETURNS TEXT
        LANGUAGE 'plpgsql'
        AS $BODY$
            DECLARE
                preferred_label     TEXT := '';
                normalized_lang_id  TEXT;
                base_lang_id        TEXT;
            BEGIN
                IF item_id IS NULL THEN
                    RETURN preferred_label;
                END IF;

                normalized_lang_id := replace(language_id, '_', '-');
                base_lang_id := split_part(normalized_lang_id, '-', 1);

                SELECT v.value
                INTO preferred_label
                FROM  arches_controlled_lists_listitemvalue v
                JOIN arches_controlled_lists_listitem i ON v.list_item_id = i.id
                WHERE i.id = item_id
                ORDER BY
                    (CASE
                        WHEN v.valuetype_id = 'prefLabel' THEN 10
                        WHEN v.valuetype_id = 'altLabel' THEN 4
                        ELSE 1
                    END) *
                    (CASE
                        WHEN v.languageid = normalized_lang_id THEN 10
                        WHEN v.languageid = base_lang_id THEN 5
                        ELSE 2
                    END
                    ) DESC
                LIMIT 1;
                IF preferred_label IS NULL THEN
                    preferred_label := '';
                END IF;
                RETURN preferred_label;
            END;
        $BODY$;

        CREATE OR REPLACE FUNCTION __arches_get_reference_label(
            nodevalue JSONB,
            language_id TEXT DEFAULT 'en'
        )
        RETURNS TEXT
        LANGUAGE 'plpgsql'
        AS $BODY$
            DECLARE
                reference_label     TEXT;
                preferred_label     TEXT := '';
                reference_data      JSONB;
                reference           JSONB;
            BEGIN
                IF nodevalue IS NULL THEN
                    RETURN '';
                END IF;
                FOREACH reference_data IN ARRAY ARRAY(SELECT jsonb_array_elements(nodevalue)) LOOP
                    preferred_label = __arches_get_preferred_label((reference_data -> 'labels' -> 0 ->> 'list_item_id')::UUID, language_id);
                    reference_label := CONCAT_WS(', ', reference_label, preferred_label);
                END LOOP;                    
                RETURN reference_label;
            END;                            
        $BODY$;

        CREATE OR REPLACE FUNCTION public.__arches_get_node_display_value(
            in_tiledata JSONb,
            in_nodeid UUID,
            language_id TEXT DEFAULT 'en')
        RETURNS TEXT
        LANGUAGE 'plpgsql'
        AS $BODY$
            DECLARE
                display_value   TEXT := '';
                in_node_type    TEXT;
                in_node_config  JSON;
            begin
                IF in_nodeid IS NULL OR in_nodeid IS NULL THEN
                    RETURN '<invalid_nodeid>';
                END IF;

                IF in_tiledata IS NULL THEN
                    RETURN '';
                END IF;

                SELECT n.datatype, n.config
                INTO in_node_type, in_node_config
                FROM nodes n WHERE nodeid = in_nodeid::UUID;

                IF in_node_type IN ('semantic', 'geoJSON-feature-collection', 'annotation') THEN
                    RETURN 'unsupported node type (' || in_node_type || ')';
                END IF;

                IF in_node_type IS NULL THEN
                    RETURN '';
                END IF;

                CASE in_node_type
                    WHEN 'string' THEN
                        display_value := ((in_tiledata -> in_nodeid::TEXT) -> language_id) ->> 'value';
                    WHEN 'concept' THEN
                        display_value := __arches_get_concept_label((in_tiledata ->> in_nodeid::TEXT)::UUID);
                    WHEN 'concept-list' THEN
                        display_value := __arches_get_concept_list_label(in_tiledata -> in_nodeid::TEXT);
                    WHEN 'reference' THEN
                        display_value := __arches_get_reference_label(in_tiledata -> in_nodeid::TEXT, language_id);
                    WHEN 'edtf' THEN
                        display_value := (in_tiledata ->> in_nodeid::TEXT);
                    WHEN 'file-list' THEN
                        display_value := __arches_get_file_list_label(in_tiledata -> in_nodeid::TEXT, language_id);
                    WHEN 'domain-value' THEN
                        display_value := __arches_get_domain_label((in_tiledata ->> in_nodeid::TEXT)::UUID, in_nodeid, language_id);
                    WHEN 'domain-value-list' THEN
                        display_value := __arches_get_domain_list_label(in_tiledata -> in_nodeid::TEXT, in_nodeid, language_id);
                    WHEN 'url' THEN
                        display_value := ((in_tiledata -> in_nodeid::TEXT)::JSONB ->> 'url');
                    WHEN 'node-value' THEN
                        display_value := __arches_get_nodevalue_label(in_tiledata -> in_nodeid::TEXT, in_nodeid);
                    WHEN 'resource-instance' THEN
                        display_value := __arches_get_resourceinstance_label(in_tiledata -> in_nodeid::TEXT, 'name', language_id);
                    WHEN 'resource-instance-list' THEN
                        display_value := __arches_get_resourceinstance_list_label(in_tiledata -> in_nodeid::TEXT, 'name', language_id);
                    ELSE
                        display_value := (in_tiledata ->> in_nodeid::TEXT)::TEXT;
                    END CASE;

                RETURN display_value;
            END;
        $BODY$;
    """

    reverse_sql = """
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
                        display_value := __arches_get_nodevalue_label(in_tiledata -> in_nodeid::text, in_nodeid);
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

        DROP FUNCTION IF EXISTS __arches_get_reference_label(JSONB, TEXT);
        DROP FUNCTION IF EXISTS __arches_get_preferred_label(UUID, TEXT);
    """

    operations = [
        migrations.RunSQL(
            sql=forward_sql,
            reverse_sql=reverse_sql,
        ),
    ]
