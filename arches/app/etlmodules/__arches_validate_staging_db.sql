CREATE OR REPLACE FUNCTION public.__arches_validate_staging_db(graph_id TEXT)
RETURNS TABLE(id INTEGER, error_message JSONB) AS
$$
	DECLARE
		node_name TEXT;
		node_id UUID;
		node_datatype TEXT;
		datatype TEXT;
		warning_message TEXT;
		header_name TEXT;
		cursor_node_name REFCURSOR;
		node_value TEXT;

	BEGIN
		UPDATE etl_staging SET message = NULL;
		FOR node_name in SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = 'etl_staging'
		LOOP
			IF node_name <> 'id' AND node_name <> 'valid' AND node_name <> 'message' THEN
				SELECT n.nodeid FROM nodes n INTO node_id WHERE lower(n.name) = node_name AND n.graphid::TEXT = graph_id;
				SELECT n.datatype FROM nodes n INTO node_datatype WHERE lower(n.name) = node_name AND n.graphid::TEXT = graph_id;
				
				CASE node_datatype
					WHEN 'number' THEN datatype = 'numeric';
					WHEN 'boolean' THEN datatype = 'boolean';
					WHEN 'resource-instance' THEN datatype = 'jsonb';
					WHEN 'resource-instance-list' THEN datatype = 'jsonb';
					WHEN 'annotation' THEN datatype = 'jsonb';
					WHEN 'file-list' THEN datatype = 'jsonb';
					WHEN 'url' THEN datatype = 'jsonb';
					WHEN 'node-value' THEN datatype = 'uuid';
					WHEN 'domain-value' THEN datatype = 'uuid';
					WHEN 'concept' THEN datatype = 'uuid';
					WHEN 'geojson-feature-collection' THEN datatype = 'geometry';
					WHEN 'date' THEN datatype = 'timestamp';
					WHEN 'domain-value-list' THEN datatype = 'uuid[]';
					WHEN 'concept-list' THEN datatype = 'uuid[]';
					ELSE datatype = 'text';
				END CASE;

				OPEN cursor_node_name FOR EXECUTE format('SELECT %s FROM etl_staging;', node_name);
				LOOP
					FETCH cursor_node_name INTO node_value;
					EXIT WHEN NOT FOUND;
					BEGIN
						EXECUTE format('SELECT %L::%s', node_value, datatype);
						EXCEPTION
							WHEN invalid_text_representation
							THEN
								GET STACKED DIAGNOSTICS warning_message = MESSAGE_TEXT;
								RAISE NOTICE '%', warning_message;
								UPDATE etl_staging
								SET message = CONCAT_WS(',',
									message,
									FORMAT('"%s": {"%s": %s}', node_name, split_part(warning_message, ':', 1), split_part(warning_message, ':', 2))
								)
								WHERE CURRENT OF cursor_node_name;
							WHEN OTHERS
							THEN
								GET STACKED DIAGNOSTICS warning_message = MESSAGE_TEXT;
								RAISE NOTICE '%', warning_message;
								UPDATE etl_staging
								SET message = CONCAT_WS(',', message, FORMAT('%s: {"error": %s}', node_name, warning_message))
								WHERE CURRENT OF cursor_node_name;
					END;
				END LOOP;
				CLOSE cursor_node_name;
			END IF;
		END LOOP;

		UPDATE etl_staging SET valid = false WHERE message IS NOT NULL;
		UPDATE etl_staging SET valid = true WHERE message IS NULL;
		UPDATE etl_staging SET message = FORMAT('{%s}', message) WHERE message IS NOT NULL;
 		RETURN QUERY
		SELECT e.id, e.message::JSONB FROM etl_staging e WHERE e.message IS NOT NULL;
    END;
$$
LANGUAGE plpgsql
