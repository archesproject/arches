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