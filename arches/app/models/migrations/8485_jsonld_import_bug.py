from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "8042_3_spatialview_db_functions"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE FUNCTION __arches_get_concept_value_from_id_or_label(
                concept_identifier text default '',
                lang text default '',
                label text default '',
                default_lang text default ''
            ) returns TABLE(score integer, valueid uuid, value text, conceptid uuid, valuetype text, languageid text) as $$
            DECLARE
                -- while some of the arguments are optional you need at least one of "concept_identifier" or "label"
                -- EG: __arches_get_concept_value_from_id_or_label("http://localhost:8000/concepts/037daf4d-054a-44d2-9c0a-108b59e39109", "en", "annotations", "en")
                -- EG: __arches_get_concept_value_from_id_or_label("http://vocab.getty.edu/aat/300047196", "de", "Gerumpelplastik", "en")
                --
                -- Arguments:
                -- concept_identifier (optional) -- can be uuid of concept, url of concept that contains a uuid, 
                --      or external identifier like http://vocab.getty.edu/aat/300047196
                -- lang -- language code
                -- label (optional) -- prefLabel, altLabel, etc..  of concept
                -- default_lang (optional) -- default language of the system, usually from settings.py LANGUAGE_CODE
                short_lang text = split_part((split_part(lang, '-', 1)), '_', 1) || '%';
                dynsql text;
                concept_id uuid;
                matches uuid;
                where_clause text;
                val record;
            BEGIN
                concept_id = (regexp_matches(concept_identifier, '([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})'))[1];
                IF concept_id IS null THEN
                    SELECT v.conceptid 
                    INTO concept_id
                    FROM values v 
                    WHERE v.value = concept_identifier AND v.valuetype = 'identifier' limit 1;
                END IF;

                RETURN QUERY(
                SELECT (
                    CASE 
                    WHEN v.languageid = lang AND v.valuetype = 'prefLabel' THEN 20
                    WHEN v.languageid like short_lang AND v.valuetype = 'prefLabel' THEN 15
                    WHEN v.languageid = lang THEN 10 
                    WHEN v.languageid like short_lang THEN 5
                    WHEN v.languageid like default_lang THEN 2
                    ELSE 0
                    END
                ) as score,
                    v.valueid, v.value, v.conceptid, v.valuetype, v.languageid
                FROM values v JOIN d_value_types dtypes ON v.valuetype = dtypes.valuetype
                WHERE (v.conceptid = concept_id OR v.value = label)
                    AND dtypes.category = 'label'
                ORDER BY score desc 
                LIMIT 5);

            END;
            $$ language plpgsql volatile;
            """,
            reverse_sql="""
            DROP FUNCTION __arches_get_concept_value_from_id_or_label(text, text, text, text); 
            """,
        )
    ]
