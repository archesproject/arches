    CREATE OR REPLACE FUNCTION public.__arches_load_staging_get_tile_errors(json_obj jsonb)
    RETURNS text
    LANGUAGE plpgsql AS

    $$
    DECLARE
        _key   text;
        _value jsonb;
        _result text;
        _note text;

    BEGIN
        FOR _key, _value IN
            SELECT * FROM jsonb_each_text($1)
        LOOP
            IF _value ->> 'valid' = 'false' THEN
                IF _value ->> 'notes' IS NULL THEN
                    _note = 'unspecified error';
                END IF;
                -- we could add the nodeid (_key), but let's not be verbose just yet
                IF _result IS NULL THEN
                _result := _value ->> 'notes';
                ELSE
                _result := '|' || (_value ->> 'notes');
                END IF;
            END IF;
        END LOOP;
        RETURN _result;
    END;
    $$;
