from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("models", "10804_core_search_filters"),
    ]

    add_bulk_concept_editor = """
        INSERT INTO etl_modules (
            etlmoduleid,
            name,
            description,
            etl_type,
            component,
            componentname,
            modulename,
            classname,
            config,
            reversible,
            icon,
            slug,
            helpsortorder,
            helptemplate
        )
        VALUES (
            '87ce44cd-3935-49fb-a9ff-37b256d23ec9',
            'Bulk Replace Concept',
            'Replace concept',
            'edit',
            'views/components/etl_modules/bulk_edit_concept',
            'bulk_edit_concept',
            'bulk_edit_concept.py',
            'BulkConceptEditor',
            '{ "bgColor": "#f5c60a", "circleColor": "#f9dd6c", "updateLimit": 5000, "previewLimit": 5, "show": true }',
            true,
            'fa fa-edit',
            'bulk_edit_concept',
            9,
            'bulk-edit-concept-help'
        )
    """
    remove_bulk_concept_editor = """
        DELETE FROM load_staging WHERE loadid IN (SELECT loadid FROM load_event WHERE etl_module_id = '87ce44cd-3935-49fb-a9ff-37b256d23ec9');
        DELETE FROM load_event WHERE etl_module_id = '87ce44cd-3935-49fb-a9ff-37b256d23ec9';
        DELETE FROM etl_modules WHERE etlmoduleid = '87ce44cd-3935-49fb-a9ff-37b256d23ec9';
    """

    add_functions_to_edit_concepts = """
        CREATE OR REPLACE FUNCTION __arches_build_staged_data(
            staged_data jsonb,
            nodeid text,
            data_type text,
            value jsonb
        )
        RETURNS jsonb
        LANGUAGE 'plpgsql'
        AS 
        $$
            DECLARE
                edited_data jsonb;
                valid boolean;
            BEGIN
                valid = true;
                edited_data = JSONB_SET(
                    staged_data,
                    FORMAT('{%s}', nodeid)::text[],
                    JSONB_BUILD_OBJECT(
                        'notes', '',
                        'valid', valid,
                        'source', 'bulk_edit',
                        'datatype', data_type,
                        'value', value
                    ),
                    true
                );
                RETURN edited_data;
            END;
        $$;

        CREATE OR REPLACE FUNCTION __arches_edit_staged_concept(
            load_id uuid,
            node_id uuid,
            old_id text,
            new_id text
        )
        RETURNS void
        LANGUAGE 'plpgsql'
        AS 
        $$
            DECLARE
                data_type text;
                updated_staged_data jsonb;
                updated_value jsonb;
                staged_record record;
                _key text;
                _value text;
            BEGIN
                FOR staged_record IN (SELECT value, tileid FROM load_staging WHERE loadid = load_id) LOOP
                    updated_staged_data = '{}'::jsonb;
                    FOR _key, _value IN SELECT * FROM jsonb_each(staged_record.value) LOOP
                        SELECT datatype INTO data_type FROM nodes WHERE nodeid = _key::uuid;
                        updated_value = _value::jsonb;
                        IF _key::uuid = node_id THEN
                            IF _value::jsonb ? old_id AND _value::jsonb ? new_id THEN
                                updated_value = _value::jsonb - old_id;
                            ELSE
                                updated_value = (REPLACE(_value, old_id, new_id))::jsonb;
                            END IF;
                        END IF;
                        updated_staged_data = __arches_build_staged_data(
                            updated_staged_data, _key, data_type, updated_value
                        );
                        UPDATE load_staging
                        SET value = updated_staged_data
                        WHERE loadid = load_id AND tileid = staged_record.tileid;
                    END LOOP;
                END LOOP;
            END;
        $$;
    """

    remove_functions_to_edit_concepts = """
        DROP FUNCTION __arches_build_staged_data(jsonb, text, text, jsonb);
        DROP FUNCTION __arches_edit_staged_concept(uuid, uuid, text, text);
    """

    operations = [
        migrations.RunSQL(
            add_bulk_concept_editor,
            remove_bulk_concept_editor,
        ),
        migrations.RunSQL(
            add_functions_to_edit_concepts,
            remove_functions_to_edit_concepts,
        ),
    ]
