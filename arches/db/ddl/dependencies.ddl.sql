/* $PostgreSQL: pgsql/contrib/uuid-ossp/uuid-ossp.sql.in,v 1.6 2007/11/13 04:24:29 momjian Exp $ */

-- Adjust this setting to control where the objects get created.
SET search_path = public;

CREATE OR REPLACE FUNCTION uuid_nil()
RETURNS uuid
AS '$libdir/uuid-ossp', 'uuid_nil'
IMMUTABLE STRICT LANGUAGE C;

CREATE OR REPLACE FUNCTION uuid_ns_dns()
RETURNS uuid
AS '$libdir/uuid-ossp', 'uuid_ns_dns'
IMMUTABLE STRICT LANGUAGE C;

CREATE OR REPLACE FUNCTION uuid_ns_url()
RETURNS uuid
AS '$libdir/uuid-ossp', 'uuid_ns_url'
IMMUTABLE STRICT LANGUAGE C;

CREATE OR REPLACE FUNCTION uuid_ns_oid()
RETURNS uuid
AS '$libdir/uuid-ossp', 'uuid_ns_oid'
IMMUTABLE STRICT LANGUAGE C;

CREATE OR REPLACE FUNCTION uuid_ns_x500()
RETURNS uuid
AS '$libdir/uuid-ossp', 'uuid_ns_x500'
IMMUTABLE STRICT LANGUAGE C;

CREATE OR REPLACE FUNCTION uuid_generate_v1()
RETURNS uuid
AS '$libdir/uuid-ossp', 'uuid_generate_v1'
VOLATILE STRICT LANGUAGE C;

CREATE OR REPLACE FUNCTION uuid_generate_v1mc()
RETURNS uuid
AS '$libdir/uuid-ossp', 'uuid_generate_v1mc'
VOLATILE STRICT LANGUAGE C;

CREATE OR REPLACE FUNCTION uuid_generate_v3(namespace uuid, name text)
RETURNS uuid
AS '$libdir/uuid-ossp', 'uuid_generate_v3'
IMMUTABLE STRICT LANGUAGE C;

CREATE OR REPLACE FUNCTION uuid_generate_v4()
RETURNS uuid
AS '$libdir/uuid-ossp', 'uuid_generate_v4'
VOLATILE STRICT LANGUAGE C;

CREATE OR REPLACE FUNCTION uuid_generate_v5(namespace uuid, name text)
RETURNS uuid
AS '$libdir/uuid-ossp', 'uuid_generate_v5'
IMMUTABLE STRICT LANGUAGE C;

--for backward compatibility with postgis 1.5 ...statement just fails in 2.0
INSERT INTO geometry_columns(
            f_table_catalog, f_table_schema, f_table_name, f_geometry_column, 
            coord_dimension, srid, "type")
    VALUES ('','app', 'geometries', 'geometry', 2, 4326, 'GEOMETRY');


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

-- Function: isstring(text)

-- DROP FUNCTION isstring(text);

-- Adjust this setting to control where the objects get created.
SET search_path = public;

CREATE OR REPLACE FUNCTION isstring("value" text)
  RETURNS text AS
$BODY$
Declare IsInt integer :=0;
BEGIN
 IsInt = Value::int;
 return 'Int';
Exception 
	when data_exception then
	return 'str';
End;

  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION isstring(text) OWNER TO postgres;