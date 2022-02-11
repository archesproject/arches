CREATE OR REPLACE PROCEDURE public.__arches_create_staging_db(headers text[]) AS $$

    DECLARE
		header text;
        query_string text;

    BEGIN
		headers := ARRAY[headers];
        FOREACH header IN ARRAY headers LOOP
			query_string := CONCAT_WS(', ', query_string, concat(header, ' TEXT'));
		END LOOP;

		DROP TABLE IF EXISTS etl_staging;
		EXECUTE format('
			CREATE TABLE etl_staging (
				id serial PRIMARY KEY,
			   	%s,
				valid boolean,
				message TEXT
			  )', query_string);
    END;

$$
LANGUAGE plpgsql