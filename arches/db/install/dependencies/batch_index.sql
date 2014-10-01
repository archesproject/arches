CREATE OR REPLACE FUNCTION BatchIndex(sn text, tn text, cn text) RETURNS void AS $$
DECLARE i_exists integer;
DECLARE idxname text;
BEGIN
  idxname := 'idx_' || tn || '_' || cn;
  select into i_exists count(*) from pg_class where relname = idxname;

  IF i_exists = 0 THEN
    EXECUTE 'CREATE INDEX ' ||idxname || ' ON '
      || sn || '.' || tn
      || ' USING GIST(' || cn || ')';
  END IF;
END;
$$ LANGUAGE plpgsql;

select BatchIndex(f_table_schema, f_table_name, f_geometry_column) from public.geometry_columns;