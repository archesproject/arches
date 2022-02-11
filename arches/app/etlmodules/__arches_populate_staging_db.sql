CREATE OR REPLACE PROCEDURE public.__arches_populate_staging_db(headers text[], nodevalues text[]) AS $$

    DECLARE
		header text;
		header_string text;
		nodevalue text;
        value_string text;

    BEGIN
        FOREACH header IN ARRAY headers LOOP
			header_string := CONCAT_WS(', ', header_string, header);
		END LOOP;

        FOREACH nodevalue IN ARRAY nodevalues LOOP
			value_string := CONCAT_WS(', ', value_string, format('%L', nodevalue));
		END LOOP;

 		EXECUTE format('INSERT INTO etl_staging (%s) VALUES (%s)', header_string, value_string);
 		COMMIT;
		
    END;

$$
LANGUAGE plpgsql
