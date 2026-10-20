from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("arches_controlled_lists", "0005_add_reference_select_widget_mapping"),
    ]

    forward_sql = """
        CREATE OR REPLACE FUNCTION __arches_controlled_lists_get_preferred_label(
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
                    END) DESC
                LIMIT 1;
                IF preferred_label IS NULL THEN
                    preferred_label := '';
                END IF;
                RETURN preferred_label;
            END;
        $BODY$;

        CREATE OR REPLACE FUNCTION __arches_controlled_lists_get_reference_label_list(
            nodevalue JSONB,
            language_id TEXT DEFAULT 'en'
        )
        RETURNS JSONB
        LANGUAGE 'plpgsql'
        AS $BODY$
            DECLARE
                labels_jsonb jsonb := '[]'::jsonb;
            BEGIN
                IF jsonb_typeof(nodevalue) != 'array' THEN
                    RETURN labels_jsonb;
                END IF;
                
                SELECT COALESCE(jsonb_agg(label), '[]'::jsonb)
                INTO labels_jsonb
                FROM (
                    SELECT __arches_controlled_lists_get_preferred_label(
                        (reference_data -> 'labels' -> 0 ->> 'list_item_id')::UUID,
                        language_id
                    ) AS label
                    FROM jsonb_array_elements(nodevalue) AS reference_data
                ) sub;
    
                RETURN labels_jsonb;
            END;
        $BODY$;
    """

    reverse_sql = """
        DROP FUNCTION IF EXISTS __arches_controlled_lists_get_reference_label_list(JSONB, TEXT);
        DROP FUNCTION IF EXISTS __arches_controlled_lists_get_preferred_label(UUID, TEXT);
    """

    operations = [
        migrations.RunSQL(
            sql=forward_sql,
            reverse_sql=reverse_sql,
        ),
    ]
