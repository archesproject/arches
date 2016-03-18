--
-- PostgreSQL database dump
--

-- Dumped from database version 9.1.4
-- Dumped by pg_dump version 9.1.4
-- Started on 2014-03-20 14:56:50

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

--
-- TOC entry 9 (class 2615 OID 15704193)
-- Name: concepts; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA concepts;


ALTER SCHEMA concepts OWNER TO postgres;

--
-- TOC entry 10 (class 2615 OID 15704194)
-- Name: data; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA data;


ALTER SCHEMA data OWNER TO postgres;

--
-- TOC entry 11 (class 2615 OID 15704195)
-- Name: ontology; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA ontology;


ALTER SCHEMA ontology OWNER TO postgres;


SET search_path = concepts, pg_catalog;

--
-- TOC entry 1259 (class 1255 OID 15704200)
-- Dependencies: 9 1863
-- Name: get_conceptid(text); Type: FUNCTION; Schema: concepts; Owner: postgres
--

CREATE FUNCTION get_conceptid(p_label text) RETURNS uuid
    LANGUAGE plpgsql
    AS $$

Declare
v_return text;

BEGIN

 v_return = (
select a.conceptid 
from concepts.concepts a, concepts.values b
where 1=1
and b.valuetype = 'prefLabel'
and b.value = p_label
and b.conceptid = a.conceptid
LIMIT 1
);

Return v_return;

End;

  $$;


ALTER FUNCTION concepts.get_conceptid(p_label text) OWNER TO postgres;

--
-- TOC entry 1261 (class 1255 OID 15704202)
-- Dependencies: 9 1863
-- Name: get_datatype(text); Type: FUNCTION; Schema: concepts; Owner: postgres
--

CREATE FUNCTION get_datatype(value text) RETURNS text
    LANGUAGE plpgsql
    AS $$
Declare v_isnumeric numeric :=0;

BEGIN
 v_isnumeric = Value::numeric;
 return 'numeric';

Exception 
	when data_exception then
	 if (select st_astext(st_geomfromtext(value)) = value) then
	 return 'geometry';

	 else return 'text';
	 
	 end if;

	  
	
End;

  $$;


ALTER FUNCTION concepts.get_datatype(value text) OWNER TO postgres;

--
-- TOC entry 1262 (class 1255 OID 15704203)
-- Dependencies: 9 1863
-- Name: get_legacyoid_from_entitytypeid(text); Type: FUNCTION; Schema: concepts; Owner: postgres
--

CREATE FUNCTION get_legacyoid_from_entitytypeid(p_entitytypeid text) RETURNS text
    LANGUAGE plpgsql
    AS $$

Declare
v_return text;

BEGIN

 v_return = (
	select b.legacyoid
	from data.entity_types a, concepts.concepts b
	where 1=1
	 and a.entitytypeid = p_entitytypeid
	 and a.conceptid = b.conceptid
);

Return v_return;

End;

  $$;


ALTER FUNCTION concepts.get_legacyoid_from_entitytypeid(p_entitytypeid text) OWNER TO postgres;

--
-- TOC entry 1263 (class 1255 OID 15704204)
-- Dependencies: 9 1863
-- Name: get_preferred_label(uuid); Type: FUNCTION; Schema: concepts; Owner: postgres
--

CREATE FUNCTION get_preferred_label(p_conceptid uuid) RETURNS text
    LANGUAGE plpgsql
    AS $$

Declare
v_return text;

BEGIN

 v_return = (
select b.value
 
from concepts.values b, concepts.d_languages c
where 1=1
and b.conceptid = p_conceptid
and b.valuetype = 'prefLabel'
and b.languageid = c.languageid
and c.isdefault = true
);

Return v_return;

End;

  $$;


ALTER FUNCTION concepts.get_preferred_label(p_conceptid uuid) OWNER TO postgres;

--
-- TOC entry 1264 (class 1255 OID 15704205)
-- Dependencies: 9 1863
-- Name: get_preferred_label(uuid, text); Type: FUNCTION; Schema: concepts; Owner: postgres
--

CREATE FUNCTION get_preferred_label(p_conceptid uuid, p_languageid text) RETURNS text
    LANGUAGE plpgsql
    AS $$

Declare
v_return text;

BEGIN

 v_return = (
select b.label 
from concepts.values b
where 1=1
and b.conceptid = p_conceptid
and b.valuetype = 'prefLabel'
and b.languageid = p_languageid
);

Return v_return;

End;

  $$;


ALTER FUNCTION concepts.get_preferred_label(p_conceptid uuid, p_languageid text) OWNER TO postgres;

--
-- TOC entry 1266 (class 1255 OID 15704207)
-- Dependencies: 9 1863
-- Name: insert_concept(text, text, text, text, text); Type: FUNCTION; Schema: concepts; Owner: postgres
--

CREATE FUNCTION insert_concept(p_label text, p_note text, p_languageid text, p_legacyid text, p_nodetype text) RETURNS uuid
    LANGUAGE plpgsql
    AS $$
    Declare
    v_conceptid uuid = public.uuid_generate_v1mc();
    v_valueid uuid = public.uuid_generate_v1mc();
    --user passes in the language for label and note language
    v_languageid text = p_languageid;
    
BEGIN

    INSERT INTO concepts.concepts(conceptid, nodetype, legacyoid) VALUES (v_conceptid, p_nodetype, p_legacyid);

    IF trim(p_label) is not null and p_label<>'' then
      INSERT INTO concepts.values (valueid, conceptid, valuetype, value, languageid)
      VALUES (v_valueid, v_conceptid, 'prefLabel', trim(initcap(p_label)), v_languageid);
    END IF;

    IF trim(p_note) is not null and p_note <> '' then 
      INSERT INTO concepts.values (valueid, conceptid, valuetype, value, languageid)
      VALUES (v_valueid, v_conceptid, 'scopeNote', p_note, v_languageid);
    END IF;  

    return v_conceptid;
-- END IF;
    
END;
$$;


ALTER FUNCTION concepts.insert_concept(p_label text, p_note text, p_languageid text, p_legacyid text, p_nodetype text) OWNER TO postgres;

--
-- TOC entry 1268 (class 1255 OID 15704209)
-- Dependencies: 9 1863
-- Name: insert_relation(text, text, text, text, text); Type: FUNCTION; Schema: concepts; Owner: postgres
--

CREATE FUNCTION insert_relation(p_legacyid1 text, p_relationtype text, p_legacyid2 text) RETURNS text
    LANGUAGE plpgsql
    AS $$

    Declare 
    v_conceptidfrom uuid = null;
    v_conceptidto uuid = null;
    
BEGIN

    v_conceptidfrom = (select conceptid from concepts.concepts c
         where trim(legacyoid) = trim(p_legacyid1));

    v_conceptidto = (select conceptid from concepts.concepts c
         where trim(legacyoid) = trim(p_legacyid2));

    IF v_conceptidfrom is not null and v_conceptidto is not null and v_conceptidto <> v_conceptidfrom and v_conceptidfrom::text||v_conceptidto::text NOT IN (SELECT conceptidfrom::text||conceptidto::text FROM concepts.relations) then
      INSERT INTO concepts.relations(relationid, conceptidfrom, conceptidto, relationtype)
      VALUES (uuid_generate_v1mc(), v_conceptidfrom, v_conceptidto, p_relationtype);
    
      return 'success!';
  
    ELSE
      return 'fail! no relation inserted.';
    END IF;

END;
$$;


ALTER FUNCTION concepts.insert_relation(p_legacyid1 text, p_relationtype text, p_legacyid2 text) OWNER TO postgres;

--
-- TOC entry 1269 (class 1255 OID 15704210)
-- Dependencies: 9 1863
-- Name: insert_value(text, text, text, text, text); Type: FUNCTION; Schema: concepts; Owner: postgres
--

CREATE FUNCTION insert_value(p_legacyid text, p_value text, p_valuetype text, p_datatype text) RETURNS uuid
    LANGUAGE plpgsql
    AS $$
    Declare 
    v_conceptid uuid = (select conceptid from concepts.concepts a where a.legacyoid = p_legacyid) ;
    v_valueid uuid = public.uuid_generate_v1mc();
    v_languageid text = (select languageid from concepts.d_languages where isdefault = TRUE limit 1);
    
BEGIN

IF p_valuetype in ('altLabel','changeNote','definition','editorialNote','example','hiddenLabel','historyNote','prefLabel','scopeNote', 'collector') THEN

    INSERT INTO concepts.values (valueid, conceptid, valuetype, value, languageid)
    VALUES (v_valueid, v_conceptid, p_valuetype, p_value, v_languageid);

    return v_valueid;

ELSE

    INSERT INTO concepts.values (valueid, conceptid, valuetype, value)
    VALUES (v_valueid, v_conceptid, p_valuetype, p_value);

    return v_valueid;
    
END IF;  

END;
$$;


ALTER FUNCTION concepts.insert_value(p_legacyid text, p_value text, p_valuetype text, p_datatype text) OWNER TO postgres;

--
-- TOC entry 1271 (class 1255 OID 15704212)
-- Dependencies: 1863 9
-- Name: is_timestamp(text); Type: FUNCTION; Schema: concepts; Owner: postgres
--

CREATE FUNCTION is_timestamp(p_value text) RETURNS text
    LANGUAGE plpgsql
    AS $$
Declare v_istimestamp timestamp;
BEGIN
 v_istimestamp = p_value::timestamp;
 return 'Y';
Exception
  when data_exception then
  return 'N';
End;

  $$;


ALTER FUNCTION concepts.is_timestamp(p_value text) OWNER TO postgres;

SET search_path = data, pg_catalog;

--
-- TOC entry 1272 (class 1255 OID 15704213)
-- Dependencies: 10 1863
-- Name: get_attribute(uuid, text); Type: FUNCTION; Schema: data; Owner: postgres
--

CREATE FUNCTION get_attribute(p_entityid uuid, p_entitytypeid text) RETURNS text
    LANGUAGE plpgsql
    AS $$
    DECLARE
  relations uuid;
  ret text := '';
    BEGIN
  FOR relations IN SELECT r.entityidrange FROM data.relations r WHERE r.entityiddomain = p_entityid
  LOOP
    IF EXISTS(SELECT * FROM data.strings a JOIN data.entities e ON e.entityid = a.entityid WHERE a.entityid = relations AND e.entitytypeid = p_entitytypeid) THEN
      ret = (select val FROM data.strings a JOIN data.entities e ON e.entityid = a.entityid WHERE a.entityid = relations AND e.entitytypeid = p_entitytypeid LIMIT 1);
      EXIT;
    ELSE
      ret = (SELECT data.get_attribute(relations, p_entitytypeid));
      IF ret != '' THEN 
        EXIT;
      END IF;
    END IF;
  END LOOP;
  RETURN ret;

End;
$$;


ALTER FUNCTION data.get_attribute(p_entityid uuid, p_entitytypeid text) OWNER TO postgres;

--
-- TOC entry 1273 (class 1255 OID 15704214)
-- Dependencies: 10 1863
-- Name: get_conceptid(text); Type: FUNCTION; Schema: data; Owner: postgres
--

CREATE FUNCTION get_conceptid(p_label text) RETURNS uuid
    LANGUAGE plpgsql
    AS $$

BEGIN

Return (
select conceptid from concepts.values
where 1=1
and value = p_label
and valuetype in ('prefLabel', 'altLabel'));

End;

  $$;


ALTER FUNCTION data.get_conceptid(p_label text) OWNER TO postgres;

--
-- TOC entry 1274 (class 1255 OID 15704215)
-- Dependencies: 10 1863
-- Name: get_entitytypeid(uuid); Type: FUNCTION; Schema: data; Owner: postgres
--

CREATE FUNCTION get_entitytypeid(p_entityid uuid) RETURNS text
    LANGUAGE plpgsql
    AS $$

BEGIN

return (select entitytypeid 
	from data.entities
	where 1=1
	and entityid = p_entityid);

End;

  $$;


ALTER FUNCTION data.get_entitytypeid(p_entityid uuid) OWNER TO postgres;

--
-- TOC entry 1275 (class 1255 OID 15704216)
-- Dependencies: 1863 10
-- Name: get_geometry(uuid); Type: FUNCTION; Schema: data; Owner: postgres
--

CREATE FUNCTION get_geometry(p_entityid uuid) RETURNS text
    LANGUAGE plpgsql
    AS $$
    DECLARE
  relations uuid;
  ret text := '';
    BEGIN
  FOR relations IN SELECT r.entityidrange FROM data.relations r WHERE r.entityiddomain = p_entityid
  LOOP
    IF EXISTS(SELECT * FROM data.geometries g WHERE g.entityid = relations) THEN
      ret = (select st_astext(st_multi(st_collect(g.val))) FROM data.geometries g WHERE g.entityid = relations);
      EXIT;
    ELSE
      ret = (SELECT data.get_geometry(relations));
      IF ret != '' THEN 
        EXIT;
      END IF;
    END IF;
  END LOOP;
  RETURN ret;

End;

$$;


ALTER FUNCTION data.get_geometry(p_entityid uuid) OWNER TO postgres;

--
-- TOC entry 1276 (class 1255 OID 15704217)
-- Dependencies: 10 1863
-- Name: get_label(uuid); Type: FUNCTION; Schema: data; Owner: postgres
--

CREATE FUNCTION get_label(p_labelid uuid) RETURNS text
    LANGUAGE plpgsql
    AS $$

BEGIN

Return (
select label from concepts.values
where 1=1
and valueid = p_labelid
and languageid = (SELECT languageid
		    FROM concepts.d_languages
                    WHERE isdefault = True));

End;

  $$;


ALTER FUNCTION data.get_label(p_labelid uuid) OWNER TO postgres;

--
-- TOC entry 1277 (class 1255 OID 15704218)
-- Dependencies: 10 1863
-- Name: get_label(uuid, text); Type: FUNCTION; Schema: data; Owner: postgres
--

CREATE FUNCTION get_label(p_labelid uuid, p_language text) RETURNS text
    LANGUAGE plpgsql
    AS $$

BEGIN

Return (
select label from concepts.values
where 1=1
and valueid = p_labelid
and languageid = p_language);

End;

  $$;


ALTER FUNCTION data.get_label(p_labelid uuid, p_language text) OWNER TO postgres;

--
-- TOC entry 1278 (class 1255 OID 15704219)
-- Dependencies: 10 1863
-- Name: get_labelid(text, text); Type: FUNCTION; Schema: data; Owner: postgres
--

CREATE FUNCTION get_labelid(p_label text, p_languageid text) RETURNS uuid
    LANGUAGE plpgsql
    AS $$

BEGIN

Return (
select labelid from concepts.values
where 1=1
and value = p_label
and languageid = p_languageid
and valuetype = 'prefLabel');

End;

  $$;


ALTER FUNCTION data.get_labelid(p_label text, p_languageid text) OWNER TO postgres;

--
-- TOC entry 1279 (class 1255 OID 15704220)
-- Dependencies: 10 1863
-- Name: get_labelid(text, text, text); Type: FUNCTION; Schema: data; Owner: postgres
--

CREATE FUNCTION get_labelid(p_label text, p_languageid text, p_labeltype text) RETURNS uuid
    LANGUAGE plpgsql
    AS $$

BEGIN

Return (
select labelid from concepts.values
where 1=1
and value = p_label
and languageid = p_languageid
and labeltype = p_labeltype);

End;

  $$;


ALTER FUNCTION data.get_labelid(p_label text, p_languageid text, p_labeltype text) OWNER TO postgres;

--
-- TOC entry 1280 (class 1255 OID 15704221)
-- Dependencies: 10 1863
-- Name: get_languageid(text); Type: FUNCTION; Schema: data; Owner: postgres
--

CREATE FUNCTION get_languageid(p_languagename text) RETURNS integer
    LANGUAGE plpgsql
    AS $$

BEGIN
	Return
	(select languageid 
	from concepts.d_languages
	where 1=1
	and languagename = p_languagename);
	

End;

  $$;


ALTER FUNCTION data.get_languageid(p_languagename text) OWNER TO postgres;

--
-- TOC entry 1281 (class 1255 OID 15704222)
-- Dependencies: 1863 10
-- Name: get_primaryname(uuid); Type: FUNCTION; Schema: data; Owner: postgres
--

CREATE FUNCTION get_primaryname(p_entityid uuid) RETURNS text
    LANGUAGE plpgsql
    AS $$
    DECLARE
  relations uuid;
  ret text := '';
    BEGIN
  FOR relations IN SELECT r.entityidrange FROM data.relations r WHERE r.entityiddomain = p_entityid
  LOOP
    IF EXISTS(SELECT * FROM data.strings a JOIN data.entities e ON e.entityid = a.entityid WHERE a.entityid = relations AND e.entitytypeid = 'NAME.E41') THEN
      ret = (select val FROM data.strings a JOIN data.entities e ON e.entityid = a.entityid WHERE a.entityid = relations AND e.entitytypeid = 'NAME.E41' LIMIT 1);
      EXIT;
    ELSE
      ret = (SELECT data.get_primaryname(relations));
      IF ret != '' THEN 
        EXIT;
      END IF;
    END IF;
  END LOOP;
  RETURN ret;

End;
$$;


ALTER FUNCTION data.get_primaryname(p_entityid uuid) OWNER TO postgres;

--
-- TOC entry 1282 (class 1255 OID 15704223)
-- Dependencies: 1863 10
-- Name: insert_entitytype(text, text, boolean, text, text, text, text, text, text, text, text); Type: FUNCTION; Schema: data; Owner: postgres
--

CREATE FUNCTION insert_entitytype(p_entitytypeid text, p_businesstablename text, p_publishbydefault boolean, p_icon text, p_defaultvectorcolor text, p_asset_entity text, p_note text, p_notelanguage text, p_entitynamelanguage text, p_entitynametype text, p_parentconceptlabel text) RETURNS text
    LANGUAGE plpgsql
    AS $$
    Declare 
    v_conceptid uuid = null;
    v_parentconceptid uuid = (select concepts.get_conceptid(p_parentconceptlabel));
    v_isresource boolean = FALSE;
    v_nodetype text = 'EntityType';
    
BEGIN

    IF p_entitytypeid = p_asset_entity THEN 
      v_isresource = TRUE;
    END IF;

    IF p_businesstablename = 'domains' THEN 
      v_nodetype = 'Collection';
    END IF;
    
    IF split_part(p_entitytypeid, '.', 1) != '' and split_part(p_entitytypeid, '.', 2) != '' THEN
        IF NOT EXISTS(SELECT entitytypeid FROM data.entity_types WHERE entitytypeid = p_entitytypeid) THEN

          v_conceptid = (select concepts.insert_concept (p_entitytypeid, p_note, p_notelanguage, upper(p_entitytypeid), v_nodetype));

          IF v_parentconceptid in (select conceptid from concepts.concepts) then
              INSERT INTO concepts.relations (conceptidfrom, conceptidto, relationtype, relationid)
              VALUES (v_parentconceptid, v_conceptid, 'narrower', public.uuid_generate_v1mc());

        END IF;
        
            IF p_businesstablename = '' THEN
              p_businesstablename = null;
            END IF;

            INSERT INTO data.entity_types(
                    classid, conceptid, businesstablename, publishbydefault, icon, 
                    defaultvectorcolor, entitytypeid, isresource)
            VALUES (btrim(split_part(p_entitytypeid, '.', 2)), v_conceptid, p_businesstablename, p_publishbydefault, p_icon, 
                    p_defaultvectorcolor, p_entitytypeid, v_isresource);


        
            return p_entitytypeid;

        ELSE
            return 'Entity type already exists: ' || p_entitytypeid;
        END IF;
    ELSE
        return 'Invalid entity type id: ' || p_entitytypeid;
    END IF;    

END;
$$;


ALTER FUNCTION data.insert_entitytype(p_entitytypeid text, p_businesstablename text, p_publishbydefault boolean, p_icon text, p_defaultvectorcolor text, p_asset_entity text, p_note text, p_notelanguage text, p_entitynamelanguage text, p_entitynametype text, p_parentconceptlabel text) OWNER TO postgres;

--
-- TOC entry 1283 (class 1255 OID 15704224)
-- Dependencies: 10
-- Name: is_primary_key(text); Type: FUNCTION; Schema: data; Owner: postgres
--

CREATE FUNCTION is_primary_key(tablename text) RETURNS name
    LANGUAGE sql
    AS $_$
  
SELECT               
  pg_attribute.attname
FROM pg_index, pg_class, pg_attribute 
WHERE 
  pg_class.oid = ($1)::regclass AND
  indrelid = pg_class.oid AND
  pg_attribute.attrelid = pg_class.oid AND 
  pg_attribute.attnum = any(pg_index.indkey)
  AND indisprimary;
  
$_$;


ALTER FUNCTION data.is_primary_key(tablename text) OWNER TO postgres;

--
-- TOC entry 1284 (class 1255 OID 15704225)
-- Dependencies: 1863 10
-- Name: legacyid_2_resourceid(text); Type: FUNCTION; Schema: data; Owner: postgres
--

CREATE FUNCTION legacyid_2_resourceid(p_legacyid text) RETURNS uuid
    LANGUAGE plpgsql
    AS $$

DECLARE
v_entityid uuid = (select id from data.vw_nodes
			where val = p_legacyid
			 and label = 'EXTERNAL XREF.E42');

BEGIN

if v_entityid is not null then
  RETURN (SELECT data.recurse_up_relations(v_entityid));

else
  RETURN null;

end if;



END
  $$;


ALTER FUNCTION data.legacyid_2_resourceid(p_legacyid text) OWNER TO postgres;

--
-- TOC entry 1285 (class 1255 OID 15704226)
-- Dependencies: 1863 10
-- Name: recurse_up_relations(uuid); Type: FUNCTION; Schema: data; Owner: postgres
--

CREATE FUNCTION recurse_up_relations(p_entityidrange uuid) RETURNS uuid
    LANGUAGE plpgsql
    AS $$

DECLARE
v_entityiddomain uuid = (select entityiddomain
			from data.relations
			where entityidrange = p_entityidrange);

BEGIN

IF v_entityiddomain in (select entityid from data.entities 
			where entitytypeid in (select entitytypeid from data.entity_types
						where isresource = true)) THEN
	RETURN v_entityiddomain;

ELSE 
	RETURN (SELECT data.recurse_up_relations(v_entityiddomain));

End if;

END
  $$;


ALTER FUNCTION data.recurse_up_relations(p_entityidrange uuid) OWNER TO postgres;

SET search_path = ontology, pg_catalog;

--
-- TOC entry 1286 (class 1255 OID 15704227)
-- Dependencies: 11 1863
-- Name: check_entitytypeid(text); Type: FUNCTION; Schema: ontology; Owner: postgres
--

CREATE FUNCTION check_entitytypeid(p_entitytypeid text) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE 

BEGIN 
if 
	p_entitytypeid in (select entitytypeid from data.entity_types where isresource = true)
	then  
	  RETURN 'ASSET';
else
	RETURN 'ELEMENT';

END IF;
END;
$$;


ALTER FUNCTION ontology.check_entitytypeid(p_entitytypeid text) OWNER TO postgres;

--
-- TOC entry 1287 (class 1255 OID 15704228)
-- Dependencies: 1863 11
-- Name: check_entitytypeid(text, text); Type: FUNCTION; Schema: ontology; Owner: postgres
--

CREATE FUNCTION check_entitytypeid(p_entitytypeidfrom text, p_entitytypeidto text) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE 

BEGIN 
if 
	p_entitytypeidfrom in (select entitytypeid from data.entity_types where isresource = true)
	and
	p_entitytypeidto in (select entitytypeid from data.entity_types where isresource = false)
  THEN
  RETURN 'OK';
  
else
	RETURN 'NOT OK!';

END IF;
END;
$$;


ALTER FUNCTION ontology.check_entitytypeid(p_entitytypeidfrom text, p_entitytypeidto text) OWNER TO postgres;

--
-- TOC entry 1289 (class 1255 OID 15704230)
-- Dependencies: 1863 11
-- Name: insert_mappings(text, text, text, boolean, text, text); Type: FUNCTION; Schema: ontology; Owner: postgres
--

CREATE FUNCTION insert_mappings(p_mapping text, p_mergenodeid text) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE 
  v_domain text;
  v_property text;
  v_entitytypefrom text;
  v_entitytypeto text;
  v_businesstablename_from text;
  v_businesstablename_to text;
  v_range text;
  v_mappingid text;
  v_index integer := 1;
  -- p_mapping is a comma separated string in the form:
  -- entitytypeid_from,businesstable,property_name,entitytypeid_to,businesstable,entitytypeid_from,...
  -- 'HISTORICAL_RESOURCE.E1,,P1,NAME.E41,strings,P2,NAMETYPE.E55,domains'
  v_steps text[] := regexp_split_to_array(p_mapping, ',');
BEGIN 

    v_entitytypefrom = btrim(v_steps[1]);
    v_entitytypeto = btrim(v_steps[array_upper(v_steps, 1)-1]);
    v_businesstablename_from = btrim(v_steps[2]);
    v_businesstablename_to = btrim(v_steps[array_upper(v_steps, 1)]);
    PERFORM data.insert_entitytype(v_entitytypefrom, v_businesstablename_from, 'True', '', '', v_entitytypefrom, '', 'en-US', 'en-US', 'UNK', '');
    PERFORM data.insert_entitytype(v_entitytypeto, v_businesstablename_to, 'True', '', '', v_entitytypefrom, '', 'en-US', 'en-US', 'UNK', '');
    v_mappingid = (SELECT ontology.insert_mapping(v_entitytypefrom, v_entitytypeto, p_mergenodeid));

    --WHILE v_index < ((array_length(v_steps,1)-1)/2)
    WHILE v_index < (array_length(v_steps,1)-1)
    LOOP
        v_domain = btrim(v_steps[v_index]);
        v_businesstablename_from = btrim(v_steps[v_index+1]);
        v_property = btrim(v_steps[v_index+2]);
        v_range = btrim(v_steps[v_index+3]);
        v_businesstablename_to = btrim(v_steps[v_index+4]);

        PERFORM data.insert_entitytype(v_domain, v_businesstablename_from, 'True', '', '', v_entitytypefrom, '', 'en-US', 'en-US', 'UNK', '');
        PERFORM data.insert_entitytype(v_range, v_businesstablename_to, 'True', '', '', v_entitytypefrom, '', 'en-US', 'en-US', 'UNK', '');
        PERFORM ontology.insert_rule(v_domain, v_property, v_range);
        PERFORM ontology.insert_mapping_step(v_mappingid, v_domain, v_property, v_range, v_entitytypefrom, v_entitytypeto, ((v_index+2)/3));  

        raise notice 'mapping step: % % %',v_domain, v_property, v_range;
        v_index := v_index + 3;

    END LOOP;
  
    RETURN v_index;

END;
$$;


ALTER FUNCTION ontology.insert_mappings(p_mapping text, p_mergenodeid text) OWNER TO postgres;

--
-- TOC entry 1290 (class 1255 OID 15704231)
-- Dependencies: 1863 11
-- Name: insert_mapping_step(text, text, text, text, text, text, integer); Type: FUNCTION; Schema: ontology; Owner: postgres
--

CREATE FUNCTION insert_mapping_step(p_mappingid text, p_domain text, p_property text, p_range text, p_entitytypefrom text, p_entitytypeto text, p_order integer) RETURNS text
    LANGUAGE plpgsql
    AS $$
    DECLARE 
        ret text = '';
        v_ruleid uuid = (SELECT ruleid FROM ontology.rules WHERE entitytypedomain = p_domain AND entitytyperange = p_range AND propertyid = p_property);
BEGIN
    IF (SELECT COUNT(*) FROM ontology.mapping_steps WHERE mappingid = p_mappingid::uuid AND ruleid = v_ruleid AND "order" = p_order) > 0
    THEN
        RETURN 'Failed';
    ELSE
      INSERT INTO ontology.mapping_steps(mappingstepid, mappingid, ruleid, "order")VALUES(public.uuid_generate_v1mc(), p_mappingid::uuid, v_ruleid, p_order);
      RETURN ret;    
    END IF;    

END;
$$;


ALTER FUNCTION ontology.insert_mapping_step(p_mappingid text, p_domain text, p_property text, p_range text, p_entitytypefrom text, p_entitytypeto text, p_order integer) OWNER TO postgres;

--
-- TOC entry 1291 (class 1255 OID 15704232)
-- Dependencies: 1863 11
-- Name: insert_mapping(text, text, boolean, text); Type: FUNCTION; Schema: ontology; Owner: postgres
--

CREATE FUNCTION insert_mapping(p_entityfrom text, p_entityto text, p_mergenodeid text) RETURNS text
    LANGUAGE plpgsql
    AS $$
    DECLARE v_newmappingid uuid = uuid_generate_v1mc();
BEGIN

    IF (SELECT COUNT(*) FROM ontology.mappings WHERE entitytypeidfrom = p_entityfrom AND entitytypeidto = p_entityto) > 0
    THEN
        RETURN (SELECT mappingid FROM ontology.mappings WHERE entitytypeidfrom = p_entityfrom AND entitytypeidto = p_entityto);
    ELSE
        INSERT INTO ontology.mappings (mappingid, entitytypeidfrom, entitytypeidto, mergenodeid)
        VALUES(v_newmappingid, p_entityfrom, p_entityto, p_mergenodeid);

        RETURN v_newmappingid;
    END IF; 

END;
$$;


ALTER FUNCTION ontology.insert_mapping(p_entityfrom text, p_entityto text, p_mergenodeid text) OWNER TO postgres;

--
-- TOC entry 1292 (class 1255 OID 15704233)
-- Dependencies: 1863 11
-- Name: insert_rule(text, text, text); Type: FUNCTION; Schema: ontology; Owner: postgres
--

CREATE FUNCTION insert_rule(p_domain text, p_property text, p_range text) RETURNS text
    LANGUAGE plpgsql
    AS $$
    DECLARE 
        v_newruleid uuid = uuid_generate_v1mc();
BEGIN
    IF (SELECT COUNT(*) FROM ontology.rules WHERE entitytypedomain = p_domain AND entitytyperange = p_range AND propertyid = p_property) > 0
    THEN
        RETURN (SELECT ruleid FROM ontology.rules WHERE entitytypedomain = p_domain AND entitytyperange = p_range AND propertyid = p_property);
    ELSE
        INSERT INTO ontology.rules (ruleid, propertyid, entitytypedomain, entitytyperange)
        VALUES(v_newruleid, p_property, p_domain, p_range);
        
        RETURN v_newruleid;
    END IF; 
END;
$$;


ALTER FUNCTION ontology.insert_rule(p_domain text, p_property text, p_range text) OWNER TO postgres;

--
-- TOC entry 1293 (class 1255 OID 15704234)
-- Dependencies: 1863 11
-- Name: tgr_mappings_validation(); Type: FUNCTION; Schema: ontology; Owner: postgres
--

CREATE FUNCTION tgr_mappings_validation() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
IF 
	new.entitytypeidfrom in (select entitytypeid from data.entity_types where isresource = true)
	and
	new.entitytypeidto in (select entitytypeid from data.entity_types where isresource = false)
  THEN
  RETURN NEW;

ELSE  
	IF new.entitytypeidfrom not in (select entitytypeid from data.entity_types where isresource = true) THEN
	RAISE EXCEPTION 'Invalid entitytypeidfrom. (%) needs to be an asset.', new.entitytypeidfrom;
	END IF;


	IF new.entitytypeidto not in (select entitytypeid from data.entity_types where isresource = false) THEN
	RAISE EXCEPTION 'Invalid entitytypeidto. (%) Needs to be an element.', new.entitytypeidto;
	END IF;

END IF;

END;
$$;


ALTER FUNCTION ontology.tgr_mappings_validation() OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;



CREATE TABLE public.user_profile
(
  user_id integer,
  details text
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.user_profile OWNER TO postgres;


SET search_path = concepts, pg_catalog;

--
-- TOC entry 222 (class 1259 OID 15704302)
-- Dependencies: 3341 9
-- Name: concepts; Type: TABLE; Schema: concepts; Owner: postgres; Tablespace: 
--

CREATE TABLE concepts (
    conceptid uuid NOT NULL,
    nodetype text NOT NULL,
    legacyoid text NOT NULL,
    CONSTRAINT unique_legacyoid UNIQUE (legacyoid)

);


ALTER TABLE concepts.concepts OWNER TO postgres;



--
-- TOC entry 222 (class 1259 OID 15704302)
-- Dependencies: 3341 9
-- Name: concepts; Type: TABLE; Schema: concepts; Owner: postgres; Tablespace: 
--

CREATE TABLE d_node_types (
    nodetype text NOT NULL,
    namespace text NOT NULL DEFAULT 'arches',
    CONSTRAINT pk_d_nodetypes PRIMARY KEY (nodetype)
);


ALTER TABLE concepts.concepts OWNER TO postgres;
--
-- TOC entry 224 (class 1259 OID 15704316)
-- Dependencies: 9
-- Name: d_languages; Type: TABLE; Schema: concepts; Owner: postgres; Tablespace: 
--

CREATE TABLE d_languages (
    languageid text NOT NULL,
    languagename text NOT NULL,
    isdefault boolean NOT NULL
);


ALTER TABLE concepts.d_languages OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 15704322)
-- Dependencies: 9
-- Name: d_relation_types; Type: TABLE; Schema: concepts; Owner: postgres; Tablespace:
--

CREATE TABLE d_relation_types (
    relationtype text NOT NULL,
	category text NOT NULL,
	namespace text NOT NULL DEFAULT 'arches'
);


ALTER TABLE concepts.d_relation_types OWNER TO postgres;

--
-- Table: concepts.d_value_types

-- DROP TABLE concepts.d_value_types;

CREATE TABLE concepts.d_value_types
(
  valuetype text NOT NULL,
  category text,
  description text,
  namespace text NOT NULL DEFAULT 'arches',
  datatype text,
  CONSTRAINT pk_d_valuetypes PRIMARY KEY (valuetype )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE concepts.d_value_types
  OWNER TO postgres;


--
-- TOC entry 227 (class 1259 OID 15704334)
-- Dependencies: 9
-- Name: geometries_geometryid_seq; Type: SEQUENCE; Schema: concepts; Owner: postgres
--

CREATE SEQUENCE geometries_geometryid_seq
    START WITH 101
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE concepts.geometries_geometryid_seq OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 15704336)
-- Dependencies: 9
-- Name: relations; Type: TABLE; Schema: concepts; Owner: postgres; Tablespace: 
--

CREATE TABLE relations (
    conceptidfrom uuid NOT NULL,
    conceptidto uuid NOT NULL,
    relationtype text NOT NULL,
    relationid uuid DEFAULT public.uuid_generate_v1mc() NOT NULL
);


ALTER TABLE concepts.relations OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 15704342)
-- Dependencies: 3343 9
-- Name: values; Type: TABLE; Schema: concepts; Owner: postgres; Tablespace: 
--

CREATE TABLE "values" (
    valueid uuid DEFAULT public.uuid_generate_v1mc() NOT NULL,
    conceptid uuid NOT NULL,
    valuetype text NOT NULL,
    value text NOT NULL,
    languageid text
);


ALTER TABLE concepts."values" OWNER TO postgres;



CREATE TABLE data.resource_x_resource
(
  resourcexid serial NOT NULL,
  entityid1 uuid NOT NULL DEFAULT public.uuid_generate_v1mc(),
  entityid2 uuid NOT NULL DEFAULT public.uuid_generate_v1mc(),
  notes text,
  relationshiptype uuid,
  datestarted date,
  dateended date,
  CONSTRAINT pk_rsrc_x_rsrc PRIMARY KEY (resourcexid)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data.resource_x_resource
  OWNER TO postgres;


CREATE TABLE data.edit_log
(
  editlogid uuid NOT NULL DEFAULT public.uuid_generate_v1mc(),
  resourceentitytypeid text,	
  resourceid uuid,
  attributeentitytypeid text,
  edittype text,
  oldvalue text,
  newvalue text,
  "timestamp" timestamp with time zone,  
  userid text,
  user_firstname text,
  user_lastname text,  
  user_email text,
  note text,

  CONSTRAINT pk_edit_log PRIMARY KEY (editlogid )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data.edit_log OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 15704349)
-- Dependencies: 3320 9
-- Name: vw_concepts; Type: VIEW; Schema: concepts; Owner: postgres
--

CREATE VIEW vw_concepts AS
    SELECT a.conceptid, get_preferred_label(a.conceptid) AS conceptlabel, a.legacyoid FROM concepts a ORDER BY get_preferred_label(a.conceptid);


ALTER TABLE concepts.vw_concepts OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 15704353)
-- Dependencies: 3321 9
-- Name: vw_edges; Type: VIEW; Schema: concepts; Owner: postgres
--

CREATE VIEW vw_edges AS
    SELECT relations.conceptidfrom AS source, relations.relationtype AS label, relations.conceptidto AS target, CASE WHEN (relations.relationtype = 'related'::text) THEN 'undirected'::text ELSE 'directed'::text END AS type FROM relations UNION SELECT "values".conceptid AS source, "values".valuetype AS label, "values".valueid AS target, 'directed'::text AS type FROM "values";


ALTER TABLE concepts.vw_edges OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 15704357)
-- Dependencies: 3322 9
-- Name: vw_nodes; Type: VIEW; Schema: concepts; Owner: postgres
--

CREATE VIEW vw_nodes AS
    SELECT a.conceptid AS id, get_preferred_label(a.conceptid) AS label, 'concept'::text AS nodetype FROM concepts a UNION SELECT a.valueid AS id, a.value AS label, a.valuetype AS nodetype FROM "values" a;


ALTER TABLE concepts.vw_nodes OWNER TO postgres;

CREATE VIEW vw_entitytype_domains AS 
 SELECT c.legacyoid AS entitytypeid,
    r.conceptidto AS conceptid,
    v.valueid AS id,
    v.value,
    v.valuetype,
    v.languageid,
    v1.value AS sortorder
   FROM concepts.concepts c
     JOIN concepts.relations r ON c.conceptid = r.conceptidfrom
     JOIN concepts."values" v ON r.conceptidto = v.conceptid
     LEFT JOIN ( SELECT "values".valueid,
            "values".conceptid,
            "values".valuetype,
            "values".value,
            "values".languageid
           FROM concepts."values"
          WHERE "values".valuetype = 'sortorder'::text) v1 ON r.conceptidto = v1.conceptid
  WHERE r.relationtype = 'member'::text AND (v.valuetype = ANY (ARRAY['prefLabel'::text, 'altLabel'::text, 'collector'::text]));

ALTER TABLE concepts.vw_entitytype_domains OWNER TO postgres;
SET search_path = data, pg_catalog;

--
-- TOC entry 233 (class 1259 OID 15704361)
-- Dependencies: 10
-- Name: dates; Type: TABLE; Schema: data; Owner: postgres; Tablespace: 
--

CREATE TABLE dates (
    entityid uuid NOT NULL,
    val timestamp without time zone
);


ALTER TABLE data.dates OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 15704364)
-- Dependencies: 10
-- Name: domains; Type: TABLE; Schema: data; Owner: postgres; Tablespace: 
--

CREATE TABLE domains (
    entityid uuid NOT NULL,
    val uuid
);


ALTER TABLE data.domains OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 15704367)
-- Dependencies: 3344 10
-- Name: entities; Type: TABLE; Schema: data; Owner: postgres; Tablespace: 
--

CREATE TABLE entities (
    entityid uuid DEFAULT public.uuid_generate_v1mc() NOT NULL,
    entitytypeid text
);


ALTER TABLE data.entities OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 15704374)
-- Dependencies: 3345 10
-- Name: entity_types; Type: TABLE; Schema: data; Owner: postgres; Tablespace: 
--

CREATE TABLE entity_types (
    classid text NOT NULL,
    conceptid uuid DEFAULT public.uuid_generate_v1mc() NOT NULL,
    businesstablename text,
    publishbydefault boolean NOT NULL,
    icon text,
    defaultvectorcolor text,
    entitytypeid text NOT NULL,
    isresource boolean
);


ALTER TABLE data.entity_types OWNER TO postgres;

--
-- TOC entry 257 (class 1259 OID 15704785)
-- Dependencies: 10
-- Name: files; Type: TABLE; Schema: data; Owner: postgres; Tablespace: 
--

CREATE TABLE files (
    entityid uuid NOT NULL,
    val text
);


ALTER TABLE data.files OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 15704381)
-- Dependencies: 10 1605
-- Name: geometries; Type: TABLE; Schema: data; Owner: postgres; Tablespace: 
--

CREATE TABLE geometries (
    entityid uuid NOT NULL,
    val public.geometry(Geometry,4326)
);


ALTER TABLE data.geometries OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 15704387)
-- Dependencies: 10
-- Name: numbers; Type: TABLE; Schema: data; Owner: postgres; Tablespace: 
--

CREATE TABLE numbers (
    entityid uuid NOT NULL,
    val double precision
);


ALTER TABLE data.numbers OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 15704393)
-- Dependencies: 10
-- Name: relations; Type: TABLE; Schema: data; Owner: postgres; Tablespace: 
--

CREATE TABLE relations (
    relationid integer NOT NULL,
    ruleid uuid NOT NULL,
    entityiddomain uuid NOT NULL,
    entityidrange uuid NOT NULL,
    notes text
);


ALTER TABLE data.relations OWNER TO postgres;

--
-- TOC entry 240 (class 1259 OID 15704399)
-- Dependencies: 239 10
-- Name: relations_relationid_seq; Type: SEQUENCE; Schema: data; Owner: postgres
--

CREATE SEQUENCE relations_relationid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE data.relations_relationid_seq OWNER TO postgres;

--
-- TOC entry 3471 (class 0 OID 0)
-- Dependencies: 240
-- Name: relations_relationid_seq; Type: SEQUENCE OWNED BY; Schema: data; Owner: postgres
--

ALTER SEQUENCE relations_relationid_seq OWNED BY relations.relationid;


--
-- TOC entry 241 (class 1259 OID 15704401)
-- Dependencies: 10
-- Name: strings; Type: TABLE; Schema: data; Owner: postgres; Tablespace: 
--

CREATE TABLE strings (
    entityid uuid NOT NULL,
    val text
);


ALTER TABLE data.strings OWNER TO postgres;

--
-- TOC entry 242 (class 1259 OID 15704407)
-- Dependencies: 3323 10
-- Name: vw_nodes; Type: VIEW; Schema: data; Owner: postgres
--

CREATE VIEW vw_nodes AS
    SELECT a.entitytypeid AS label, a.entityid AS id, b.val FROM (entities a LEFT JOIN ((((SELECT strings.entityid, strings.val FROM strings UNION SELECT dates.entityid, (dates.val)::text AS val FROM dates) UNION SELECT numbers.entityid, (numbers.val)::text AS val FROM numbers) UNION SELECT geometries.entityid, public.st_astext(geometries.val) AS val FROM geometries) UNION SELECT d.entityid, lbl.value AS val FROM domains d, concepts."values" lbl WHERE (((1 = 1) AND (d.val = lbl.valueid)) AND (lbl.valuetype = 'prefLabel'::text))) b ON ((a.entityid = b.entityid)));


ALTER TABLE data.vw_nodes OWNER TO postgres;

SET search_path = ontology, pg_catalog;

--
-- TOC entry 243 (class 1259 OID 15704412)
-- Dependencies: 3347 11
-- Name: rules; Type: TABLE; Schema: ontology; Owner: postgres; Tablespace: 
--

CREATE TABLE rules (
    ruleid uuid DEFAULT public.uuid_generate_v1mc() NOT NULL,
    entitytypedomain text,
    entitytyperange text,
    propertyid text NOT NULL
);


ALTER TABLE ontology.rules OWNER TO postgres;

SET search_path = data, pg_catalog;

--
-- TOC entry 244 (class 1259 OID 15704419)
-- Dependencies: 3324 10
-- Name: vw_edges; Type: VIEW; Schema: data; Owner: postgres
--

CREATE VIEW vw_edges AS
    SELECT a.id AS source, d.propertyid AS label, c.id AS target FROM vw_nodes a, relations b, vw_nodes c, ontology.rules d WHERE ((((1 = 1) AND (a.id = b.entityiddomain)) AND (b.entityidrange = c.id)) AND (b.ruleid = d.ruleid));


ALTER TABLE data.vw_edges OWNER TO postgres;

--
-- TOC entry 245 (class 1259 OID 15704423)
-- Dependencies: 3325 1605 10
-- Name: vw_resources; Type: VIEW; Schema: data; Owner: postgres
--

CREATE VIEW vw_resources AS
    SELECT row_number() OVER () AS geom_id, b.entityid AS resourceid, get_entitytypeid(b.entityid) AS rsrc_type, get_primaryname(b.entityid) AS p_name, get_attribute(b.entityid, 'SUMMARY.E62'::text) AS summary, a.val FROM ((SELECT recurse_up_relations(geometries.entityid) AS resourceid, geometries.val FROM geometries) a JOIN entities b ON ((a.resourceid = b.entityid)));


ALTER TABLE data.vw_resources OWNER TO postgres;

--
-- TOC entry 246 (class 1259 OID 15704427)
-- Dependencies: 3326 10 1605
-- Name: vw_resources_line; Type: VIEW; Schema: data; Owner: postgres
--

CREATE VIEW vw_resources_line AS
    SELECT row_number() OVER () AS geom_id, b.entityid AS resourceid, get_entitytypeid(b.entityid) AS rsrc_type, get_primaryname(b.entityid) AS p_name, get_attribute(b.entityid, 'SUMMARY.E62'::text) AS summary, a.val FROM ((SELECT recurse_up_relations(geometries.entityid) AS resourceid, geometries.val FROM geometries) a JOIN entities b ON ((a.resourceid = b.entityid))) WHERE (public.st_geometrytype(a.val) = ANY (ARRAY['ST_MultiLineString'::text, 'ST_Linestring'::text]));


ALTER TABLE data.vw_resources_line OWNER TO postgres;

--
-- TOC entry 247 (class 1259 OID 15704432)
-- Dependencies: 3327 1605 10
-- Name: vw_resources_point; Type: VIEW; Schema: data; Owner: postgres
--

CREATE VIEW vw_resources_point AS
    SELECT row_number() OVER () AS geom_id, b.entityid AS resourceid, get_entitytypeid(b.entityid) AS rsrc_type, get_primaryname(b.entityid) AS p_name, get_attribute(b.entityid, 'SUMMARY.E62'::text) AS summary, a.val FROM ((SELECT recurse_up_relations(geometries.entityid) AS resourceid, geometries.val FROM geometries) a JOIN entities b ON ((a.resourceid = b.entityid))) WHERE (public.st_geometrytype(a.val) = ANY (ARRAY['ST_MultiPoint'::text, 'ST_Point'::text]));


ALTER TABLE data.vw_resources_point OWNER TO postgres;

--
-- TOC entry 248 (class 1259 OID 15704437)
-- Dependencies: 3328 1605 10
-- Name: vw_resources_poly; Type: VIEW; Schema: data; Owner: postgres
--

CREATE VIEW vw_resources_poly AS
    SELECT row_number() OVER () AS geom_id, b.entityid AS resourceid, get_entitytypeid(b.entityid) AS rsrc_type, get_primaryname(b.entityid) AS p_name, get_attribute(b.entityid, 'SUMMARY.E62'::text) AS summary, a.val FROM ((SELECT recurse_up_relations(geometries.entityid) AS resourceid, geometries.val FROM geometries) a JOIN entities b ON ((a.resourceid = b.entityid))) WHERE (public.st_geometrytype(a.val) = ANY (ARRAY['ST_MultiPolygon'::text, 'ST_Polygon'::text]));


ALTER TABLE data.vw_resources_poly OWNER TO postgres;

SET search_path = ontology, pg_catalog;


--
-- TOC entry 250 (class 1259 OID 15704448)
-- Dependencies: 3348 11
-- Name: classes; Type: TABLE; Schema: ontology; Owner: postgres; Tablespace: 
--

CREATE TABLE classes (
    classid text NOT NULL,
    classname text NOT NULL,
    isactive boolean DEFAULT true NOT NULL
);


ALTER TABLE ontology.classes OWNER TO postgres;

--
-- TOC entry 251 (class 1259 OID 15704455)
-- Dependencies: 3349 11
-- Name: mapping_steps; Type: TABLE; Schema: ontology; Owner: postgres; Tablespace: 
--

CREATE TABLE mapping_steps (
    mappingstepid uuid DEFAULT public.uuid_generate_v1mc() NOT NULL,
    mappingid uuid NOT NULL,
    ruleid uuid DEFAULT public.uuid_generate_v1mc() NOT NULL,
    "order" integer NOT NULL
);


ALTER TABLE ontology.mapping_steps OWNER TO postgres;



--SET search_path = ontology, pg_catalog;

--
-- TOC entry 252 (class 1259 OID 15704462)
-- Dependencies: 3350 3351 11
-- Name: mappings; Type: TABLE; Schema: ontology; Owner: postgres; Tablespace: 
--

CREATE TABLE mappings (
    mappingid uuid DEFAULT public.uuid_generate_v1mc() NOT NULL,
    entitytypeidfrom text,
    entitytypeidto text,
    mergenodeid text,
  cardinality text
);



ALTER TABLE ontology.mappings OWNER TO postgres;

CREATE OR REPLACE VIEW ontology.vw_export_nodes AS 
 SELECT foo.assettype,
    foo.node AS label,
    (foo.assettype || ':'::text) || foo.node AS id,
    foo.mergenodeid AS mergenode,
    foo.businesstable AS businesstablename
   FROM ( SELECT m.entitytypeidfrom AS assettype,
            r.entitytypedomain AS node,
            m.mergenodeid,
            ( SELECT entity_types.businesstablename
                   FROM data.entity_types
                  WHERE entity_types.entitytypeid = r.entitytypedomain) AS businesstable
           FROM ontology.mapping_steps ms
             JOIN ontology.mappings m ON m.mappingid = ms.mappingid
             JOIN ontology.rules r ON r.ruleid = ms.ruleid
        UNION
         SELECT m.entitytypeidfrom,
            r.entitytyperange AS node,
            m.mergenodeid,
            ( SELECT entity_types.businesstablename
                   FROM data.entity_types
                  WHERE entity_types.entitytypeid = r.entitytyperange) AS businesstable
           FROM ontology.mapping_steps ms
             JOIN ontology.mappings m ON m.mappingid = ms.mappingid
             JOIN ontology.rules r ON r.ruleid = ms.ruleid) foo
  WHERE (foo.node <> ALL (ARRAY['ARCHES_RECORD.E31'::text, 'CREATION_EVENT.E65'::text, 'UPDATE_EVENT.E65'::text, 'COMPILER.E82'::text, 'COMPILER_PERSON.E21'::text, 'REFERENCE_NUMBER_(INTERNAL).E42'::text, 'TIME-SPAN_UPDATE_EVENT.E52'::text, 'TIME-SPAN_CREATION_EVENT.E52'::text, 'DATE_OF_COMPILATION.E50'::text, 'DATE_OF_LAST_UPDATE.E50'::text])) AND foo.node <> foo.assettype
  ORDER BY foo.assettype, foo.node;

ALTER TABLE ontology.vw_export_nodes
  OWNER TO postgres;

--SET search_path = ontology, pg_catalog;

CREATE OR REPLACE VIEW ontology.vw_export_edges AS 
 SELECT m.entitytypeidfrom AS assettype,
    (m.entitytypeidfrom || ':'::text) || r.entitytypedomain AS source,
    (m.entitytypeidfrom || ':'::text) || r.entitytyperange AS target,
    r.propertyid AS label
   FROM ontology.mapping_steps ms
     JOIN ontology.mappings m ON m.mappingid = ms.mappingid
     JOIN ontology.rules r ON r.ruleid = ms.ruleid
  WHERE (m.entitytypeidfrom <> ALL (ARRAY['ARCHES_RECORD.E31'::text, 'CREATION_EVENT.E65'::text, 'UPDATE_EVENT.E65'::text, 'COMPILER.E82'::text, 'COMPILER_PERSON.E21'::text, 'REFERENCE_NUMBER_(INTERNAL).E42'::text, 'TIME-SPAN_UPDATE_EVENT.E52'::text, 'TIME-SPAN_CREATION_EVENT.E52'::text, 'DATE_OF_COMPILATION.E50'::text, 'DATE_OF_LAST_UPDATE.E50'::text])) AND (r.entitytypedomain <> ALL (ARRAY['ARCHES_RECORD.E31'::text, 'CREATION_EVENT.E65'::text, 'UPDATE_EVENT.E65'::text, 'COMPILER.E82'::text, 'COMPILER_PERSON.E21'::text, 'REFERENCE_NUMBER_(INTERNAL).E42'::text, 'TIME-SPAN_UPDATE_EVENT.E52'::text, 'TIME-SPAN_CREATION_EVENT.E52'::text, 'DATE_OF_COMPILATION.E50'::text, 'DATE_OF_LAST_UPDATE.E50'::text])) AND (r.entitytyperange <> ALL (ARRAY['ARCHES_RECORD.E31'::text, 'CREATION_EVENT.E65'::text, 'UPDATE_EVENT.E65'::text, 'COMPILER.E82'::text, 'COMPILER_PERSON.E21'::text, 'REFERENCE_NUMBER_(INTERNAL).E42'::text, 'TIME-SPAN_UPDATE_EVENT.E52'::text, 'TIME-SPAN_CREATION_EVENT.E52'::text, 'DATE_OF_COMPILATION.E50'::text, 'DATE_OF_LAST_UPDATE.E50'::text])) AND m.entitytypeidto = r.entitytyperange
  ORDER BY m.entitytypeidfrom;

ALTER TABLE ontology.vw_export_edges
  OWNER TO postgres;
--
-- TOC entry 253 (class 1259 OID 15704470)
-- Dependencies: 11
-- Name: properties; Type: TABLE; Schema: ontology; Owner: postgres; Tablespace: 
--

CREATE TABLE properties (
    propertyid text NOT NULL,
    classdomain text NOT NULL,
    classrange text NOT NULL,
    propertydisplay text
);


ALTER TABLE ontology.properties OWNER TO postgres;

--
-- TOC entry 254 (class 1259 OID 15704476)
-- Dependencies: 3329 11
-- Name: vw_edges; Type: VIEW; Schema: ontology; Owner: postgres
--

CREATE VIEW vw_edges AS
    SELECT m.entitytypeidfrom AS assettype, ((m.entitytypeidfrom || ':'::text) || r.entitytypedomain) AS source, ((m.entitytypeidfrom || ':'::text) || r.entitytyperange) AS target, r.propertyid AS label FROM ((mapping_steps ms JOIN mappings m ON ((m.mappingid = ms.mappingid))) JOIN rules r ON ((r.ruleid = ms.ruleid))) ORDER BY m.entitytypeidfrom;


ALTER TABLE ontology.vw_edges OWNER TO postgres;

--
-- TOC entry 255 (class 1259 OID 15704480)
-- Dependencies: 3330 11
-- Name: vw_nodes; Type: VIEW; Schema: ontology; Owner: postgres
--

CREATE OR REPLACE VIEW ontology.vw_nodes AS 
 SELECT foo.assettype, foo.node AS label, (foo.assettype || ':'::text) || foo.node AS id, mergenodeid as mergenode, businesstable as businesstablename
   FROM (         SELECT m.entitytypeidfrom AS assettype, r.entitytypedomain AS node, m.mergenodeid, 
			(select businesstablename from data.entity_types where entitytypeid = r.entitytypedomain) as businesstable
                   FROM ontology.mapping_steps ms
              JOIN ontology.mappings m ON m.mappingid = ms.mappingid
         JOIN ontology.rules r ON r.ruleid = ms.ruleid
        UNION 
                 SELECT m.entitytypeidfrom, r.entitytyperange AS node, m.mergenodeid,
			(select businesstablename from data.entity_types where entitytypeid = r.entitytypedomain) as businesstable
                   FROM ontology.mapping_steps ms
              JOIN ontology.mappings m ON m.mappingid = ms.mappingid
         JOIN ontology.rules r ON r.ruleid = ms.ruleid) foo
  ORDER BY foo.assettype;

ALTER TABLE ontology.vw_nodes OWNER TO postgres;


SET search_path = data, pg_catalog;

--
-- TOC entry 3346 (class 2604 OID 15704491)
-- Dependencies: 240 239
-- Name: relationid; Type: DEFAULT; Schema: data; Owner: postgres
--

ALTER TABLE ONLY relations ALTER COLUMN relationid SET DEFAULT nextval('relations_relationid_seq'::regclass);


SET search_path = concepts, pg_catalog;

--
-- TOC entry 3373 (class 2606 OID 15704513)
-- Dependencies: 222 222
-- Name: pk_concepts; Type: CONSTRAINT; Schema: concepts; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY concepts
    ADD CONSTRAINT pk_concepts PRIMARY KEY (conceptid);


--
-- TOC entry 3379 (class 2606 OID 15704517)
-- Dependencies: 224 224
-- Name: pk_d_languages; Type: CONSTRAINT; Schema: concepts; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY d_languages
    ADD CONSTRAINT pk_d_languages PRIMARY KEY (languageid);


--
-- TOC entry 3381 (class 2606 OID 15704519)
-- Dependencies: 225 225
-- Name: pk_d_relationtypes; Type: CONSTRAINT; Schema: concepts; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY d_relation_types
    ADD CONSTRAINT pk_d_relationtypes PRIMARY KEY (relationtype);



--
-- TOC entry 3385 (class 2606 OID 15704523)
-- Dependencies: 228 228 228 228 228
-- Name: pk_relations; Type: CONSTRAINT; Schema: concepts; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY relations
    ADD CONSTRAINT pk_relations PRIMARY KEY (relationid);


--
-- TOC entry 3387 (class 2606 OID 15704525)
-- Dependencies: 229 229
-- Name: pk_values; Type: CONSTRAINT; Schema: concepts; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY "values"
    ADD CONSTRAINT pk_values PRIMARY KEY (valueid);


SET search_path = data, pg_catalog;

--
-- TOC entry 3389 (class 2606 OID 15704529)
-- Dependencies: 233 233
-- Name: pk_dates; Type: CONSTRAINT; Schema: data; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY dates
    ADD CONSTRAINT pk_dates PRIMARY KEY (entityid);


--
-- TOC entry 3391 (class 2606 OID 15704531)
-- Dependencies: 234 234
-- Name: pk_domain_values; Type: CONSTRAINT; Schema: data; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY domains
    ADD CONSTRAINT pk_domain_values PRIMARY KEY (entityid);


--
-- TOC entry 3393 (class 2606 OID 15704533)
-- Dependencies: 235 235
-- Name: pk_entities; Type: CONSTRAINT; Schema: data; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY entities
    ADD CONSTRAINT pk_entities PRIMARY KEY (entityid);


--
-- TOC entry 3395 (class 2606 OID 15704535)
-- Dependencies: 236 236
-- Name: pk_entity_types; Type: CONSTRAINT; Schema: data; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY entity_types
    ADD CONSTRAINT pk_entity_types PRIMARY KEY (entitytypeid);


--
-- TOC entry 3424 (class 2606 OID 15704792)
-- Dependencies: 257 257
-- Name: pk_files; Type: CONSTRAINT; Schema: data; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY files
    ADD CONSTRAINT pk_files PRIMARY KEY (entityid);


--
-- TOC entry 3397 (class 2606 OID 15704537)
-- Dependencies: 237 237
-- Name: pk_geometries; Type: CONSTRAINT; Schema: data; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY geometries
    ADD CONSTRAINT pk_geometries PRIMARY KEY (entityid);


--
-- TOC entry 3399 (class 2606 OID 15704539)
-- Dependencies: 238 238
-- Name: pk_numbers; Type: CONSTRAINT; Schema: data; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY numbers
    ADD CONSTRAINT pk_numbers PRIMARY KEY (entityid);


--
-- TOC entry 3401 (class 2606 OID 15704541)
-- Dependencies: 239 239
-- Name: pk_relations; Type: CONSTRAINT; Schema: data; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY relations
    ADD CONSTRAINT pk_relations PRIMARY KEY (relationid);


--
-- TOC entry 3406 (class 2606 OID 15704543)
-- Dependencies: 241 241
-- Name: pk_strings; Type: CONSTRAINT; Schema: data; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY strings
    ADD CONSTRAINT pk_strings PRIMARY KEY (entityid);


SET search_path = ontology, pg_catalog;


--
-- TOC entry 3414 (class 2606 OID 15704547)
-- Dependencies: 250 250
-- Name: pk_classes; Type: CONSTRAINT; Schema: ontology; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY classes
    ADD CONSTRAINT pk_classes PRIMARY KEY (classid);


--
-- TOC entry 3416 (class 2606 OID 15704549)
-- Dependencies: 251 251 251 251
-- Name: pk_mappings_x_rules; Type: CONSTRAINT; Schema: ontology; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY mapping_steps
    ADD CONSTRAINT pk_mappings_x_rules PRIMARY KEY (mappingstepid);


--
-- TOC entry 3422 (class 2606 OID 15704551)
-- Dependencies: 253 253
-- Name: pk_propertyid; Type: CONSTRAINT; Schema: ontology; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY properties
    ADD CONSTRAINT pk_propertyid PRIMARY KEY (propertyid);


--
-- TOC entry 3418 (class 2606 OID 15704553)
-- Dependencies: 252 252
-- Name: pk_relationships; Type: CONSTRAINT; Schema: ontology; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY mappings
    ADD CONSTRAINT pk_relationships PRIMARY KEY (mappingid);


--
-- TOC entry 3408 (class 2606 OID 15704555)
-- Dependencies: 243 243
-- Name: pk_rules; Type: CONSTRAINT; Schema: ontology; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY rules
    ADD CONSTRAINT pk_rules PRIMARY KEY (ruleid);


--
-- TOC entry 3410 (class 2606 OID 15704557)
-- Dependencies: 243 243 243 243
-- Name: uk_rules; Type: CONSTRAINT; Schema: ontology; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY rules
    ADD CONSTRAINT uk_rules UNIQUE (entitytypedomain, entitytyperange, propertyid);


--
-- TOC entry 3420 (class 2606 OID 15704559)
-- Dependencies: 252 252 252
-- Name: unique_mappings; Type: CONSTRAINT; Schema: ontology; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY mappings
    ADD CONSTRAINT unique_mappings UNIQUE (entitytypeidfrom, entitytypeidto);


ALTER TABLE ONLY mapping_steps
    ADD CONSTRAINT unique_mappingsteps UNIQUE (mappingid, ruleid, "order");


SET search_path = data, pg_catalog;

--
-- TOC entry 3402 (class 1259 OID 15704560)
-- Dependencies: 239
-- Name: relations_entityiddomain_idx; Type: INDEX; Schema: data; Owner: postgres; Tablespace: 
--

CREATE INDEX relations_entityiddomain_idx ON relations USING btree (entityiddomain);


--
-- TOC entry 3403 (class 1259 OID 15704561)
-- Dependencies: 239
-- Name: relations_entityidrange_idx; Type: INDEX; Schema: data; Owner: postgres; Tablespace: 
--

CREATE INDEX relations_entityidrange_idx ON relations USING btree (entityidrange);


--
-- TOC entry 3404 (class 1259 OID 15704562)
-- Dependencies: 239 239
-- Name: relationships_uk; Type: INDEX; Schema: data; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX relationships_uk ON relations USING btree (entityiddomain, entityidrange);


SET search_path = ontology, pg_catalog;

--
-- TOC entry 3462 (class 2620 OID 15704563)
-- Dependencies: 1293 252
-- Name: tgr_validate_entitytypes_in_mappings; Type: TRIGGER; Schema: ontology; Owner: postgres
--

CREATE TRIGGER tgr_validate_entitytypes_in_mappings BEFORE INSERT ON mappings FOR EACH ROW EXECUTE PROCEDURE tgr_mappings_validation();


SET search_path = concepts, pg_catalog;

--
-- TOC entry 3434 (class 2606 OID 15704589)
-- Dependencies: 222 3372 229
-- Name: fk_concepts_x_values; Type: FK CONSTRAINT; Schema: concepts; Owner: postgres
--

ALTER TABLE ONLY concepts
    ADD CONSTRAINT fk_concepts_x_nodetypes FOREIGN KEY (nodetype) REFERENCES d_node_types(nodetype);

--
-- TOC entry 3434 (class 2606 OID 15704589)
-- Dependencies: 222 3372 229
-- Name: fk_concepts_x_values; Type: FK CONSTRAINT; Schema: concepts; Owner: postgres
--

ALTER TABLE ONLY "values"
    ADD CONSTRAINT fk_concepts_x_values FOREIGN KEY (conceptid) REFERENCES concepts(conceptid);


--
-- TOC entry 3431 (class 2606 OID 15704599)
-- Dependencies: 228 3372 222
-- Name: fk_conceptsfrom_x_relations; Type: FK CONSTRAINT; Schema: concepts; Owner: postgres
--

ALTER TABLE ONLY relations
    ADD CONSTRAINT fk_conceptsfrom_x_relations FOREIGN KEY (conceptidfrom) REFERENCES concepts(conceptid);


--
-- TOC entry 3432 (class 2606 OID 15704604)
-- Dependencies: 3372 228 222
-- Name: fk_conceptsto_x_relations; Type: FK CONSTRAINT; Schema: concepts; Owner: postgres
--

ALTER TABLE ONLY relations
    ADD CONSTRAINT fk_conceptsto_x_relations FOREIGN KEY (conceptidto) REFERENCES concepts(conceptid);


--
-- TOC entry 3435 (class 2606 OID 15704609)
-- Dependencies: 3378 224 229
-- Name: fk_d_languages_values; Type: FK CONSTRAINT; Schema: concepts; Owner: postgres
--

ALTER TABLE ONLY "values"
    ADD CONSTRAINT fk_d_languages_values FOREIGN KEY (languageid) REFERENCES d_languages(languageid);


--
-- TOC entry 3433 (class 2606 OID 15704614)
-- Dependencies: 228 225 3380
-- Name: fk_relations_x_d_relationtypes; Type: FK CONSTRAINT; Schema: concepts; Owner: postgres
--

ALTER TABLE ONLY relations
    ADD CONSTRAINT fk_relations_x_d_relationtypes FOREIGN KEY (relationtype) REFERENCES d_relation_types(relationtype);


--
-- TOC entry 3436 (class 2606 OID 15704619)
-- Dependencies: 3382 226 229
-- Name: fk_valuetype_d_valuetype; Type: FK CONSTRAINT; Schema: concepts; Owner: postgres
--

ALTER TABLE ONLY "values"
    ADD CONSTRAINT fk_valuetype_d_valuetype FOREIGN KEY (valuetype) REFERENCES d_value_types(valuetype);


SET search_path = data, pg_catalog;

--
-- TOC entry 3441 (class 2606 OID 15704624)
-- Dependencies: 3413 236 250
-- Name: fk_classes_x_entity_types; Type: FK CONSTRAINT; Schema: data; Owner: postgres
--

ALTER TABLE ONLY entity_types
    ADD CONSTRAINT fk_classes_x_entity_types FOREIGN KEY (classid) REFERENCES ontology.classes(classid);


--
-- TOC entry 3442 (class 2606 OID 15704629)
-- Dependencies: 3372 236 222
-- Name: fk_concepts_x_entity_types; Type: FK CONSTRAINT; Schema: data; Owner: postgres
--

ALTER TABLE ONLY entity_types
    ADD CONSTRAINT fk_concepts_x_entity_types FOREIGN KEY (conceptid) REFERENCES concepts.concepts(conceptid);


--
-- TOC entry 3437 (class 2606 OID 15704634)
-- Dependencies: 233 3392 235
-- Name: fk_entities_dates; Type: FK CONSTRAINT; Schema: data; Owner: postgres
--

ALTER TABLE ONLY dates
    ADD CONSTRAINT fk_entities_dates FOREIGN KEY (entityid) REFERENCES entities(entityid);


--
-- TOC entry 3438 (class 2606 OID 15704639)
-- Dependencies: 234 3392 235
-- Name: fk_entities_domains; Type: FK CONSTRAINT; Schema: data; Owner: postgres
--

ALTER TABLE ONLY domains
    ADD CONSTRAINT fk_entities_domains FOREIGN KEY (entityid) REFERENCES entities(entityid);


--
-- TOC entry 3461 (class 2606 OID 15704793)
-- Dependencies: 3392 235 257
-- Name: fk_entities_files; Type: FK CONSTRAINT; Schema: data; Owner: postgres
--

ALTER TABLE ONLY files
    ADD CONSTRAINT fk_entities_files FOREIGN KEY (entityid) REFERENCES entities(entityid);


--
-- TOC entry 3444 (class 2606 OID 15704644)
-- Dependencies: 3392 237 235
-- Name: fk_entities_geometries; Type: FK CONSTRAINT; Schema: data; Owner: postgres
--

ALTER TABLE ONLY geometries
    ADD CONSTRAINT fk_entities_geometries FOREIGN KEY (entityid) REFERENCES entities(entityid);


--
-- TOC entry 3445 (class 2606 OID 15704649)
-- Dependencies: 238 3392 235
-- Name: fk_entities_numbers; Type: FK CONSTRAINT; Schema: data; Owner: postgres
--

ALTER TABLE ONLY numbers
    ADD CONSTRAINT fk_entities_numbers FOREIGN KEY (entityid) REFERENCES entities(entityid);


--
-- TOC entry 3446 (class 2606 OID 15704654)
-- Dependencies: 235 3392 239
-- Name: fk_entities_relations_entitydomain; Type: FK CONSTRAINT; Schema: data; Owner: postgres
--

ALTER TABLE ONLY relations
    ADD CONSTRAINT fk_entities_relations_entitydomain FOREIGN KEY (entityiddomain) REFERENCES entities(entityid);


--
-- TOC entry 3447 (class 2606 OID 15704659)
-- Dependencies: 235 239 3392
-- Name: fk_entities_relations_entityrange; Type: FK CONSTRAINT; Schema: data; Owner: postgres
--

ALTER TABLE ONLY relations
    ADD CONSTRAINT fk_entities_relations_entityrange FOREIGN KEY (entityidrange) REFERENCES entities(entityid);


--
-- TOC entry 3449 (class 2606 OID 15704664)
-- Dependencies: 3392 241 235
-- Name: fk_entities_strings; Type: FK CONSTRAINT; Schema: data; Owner: postgres
--

ALTER TABLE ONLY strings
    ADD CONSTRAINT fk_entities_strings FOREIGN KEY (entityid) REFERENCES entities(entityid);


--
-- TOC entry 3440 (class 2606 OID 15704669)
-- Dependencies: 235 236 3394
-- Name: fk_entity_types_entities; Type: FK CONSTRAINT; Schema: data; Owner: postgres
--

ALTER TABLE ONLY entities
    ADD CONSTRAINT fk_entity_types_entities FOREIGN KEY (entitytypeid) REFERENCES entity_types(entitytypeid);


--
-- TOC entry 3448 (class 2606 OID 15704679)
-- Dependencies: 239 243 3407
-- Name: fk_relations_x_rules; Type: FK CONSTRAINT; Schema: data; Owner: postgres
--

ALTER TABLE ONLY relations
    ADD CONSTRAINT fk_relations_x_rules FOREIGN KEY (ruleid) REFERENCES ontology.rules(ruleid);


--
-- TOC entry 3439 (class 2606 OID 15704684)
-- Dependencies: 229 234 3386
-- Name: fk_values_x_domains; Type: FK CONSTRAINT; Schema: data; Owner: postgres
--

ALTER TABLE ONLY domains
    ADD CONSTRAINT fk_values_x_domains FOREIGN KEY (val) REFERENCES concepts."values"(valueid);


SET search_path = ontology, pg_catalog;

--
-- TOC entry 3459 (class 2606 OID 15704699)
-- Dependencies: 250 3413 253
-- Name: fk_classes_properties_classdomain; Type: FK CONSTRAINT; Schema: ontology; Owner: postgres
--

ALTER TABLE ONLY properties
    ADD CONSTRAINT fk_classes_properties_classdomain FOREIGN KEY (classdomain) REFERENCES classes(classid);


--
-- TOC entry 3460 (class 2606 OID 15704704)
-- Dependencies: 253 250 3413
-- Name: fk_classes_properties_classrange; Type: FK CONSTRAINT; Schema: ontology; Owner: postgres
--

ALTER TABLE ONLY properties
    ADD CONSTRAINT fk_classes_properties_classrange FOREIGN KEY (classrange) REFERENCES classes(classid);


--
-- TOC entry 3450 (class 2606 OID 15704709)
-- Dependencies: 3394 243 236
-- Name: fk_entity_types_entitytypedomain; Type: FK CONSTRAINT; Schema: ontology; Owner: postgres
--

ALTER TABLE ONLY rules
    ADD CONSTRAINT fk_entity_types_entitytypedomain FOREIGN KEY (entitytypedomain) REFERENCES data.entity_types(entitytypeid);


--
-- TOC entry 3451 (class 2606 OID 15704714)
-- Dependencies: 3394 236 243
-- Name: fk_entity_types_entitytyperange; Type: FK CONSTRAINT; Schema: ontology; Owner: postgres
--

ALTER TABLE ONLY rules
    ADD CONSTRAINT fk_entity_types_entitytyperange FOREIGN KEY (entitytyperange) REFERENCES data.entity_types(entitytypeid);


--
-- TOC entry 3457 (class 2606 OID 15704719)
-- Dependencies: 252 3394 236
-- Name: fk_mappings_x_entitytypefrom; Type: FK CONSTRAINT; Schema: ontology; Owner: postgres
--

ALTER TABLE ONLY mappings
    ADD CONSTRAINT fk_mappings_x_entitytypefrom FOREIGN KEY (entitytypeidfrom) REFERENCES data.entity_types(entitytypeid);


--
-- TOC entry 3458 (class 2606 OID 15704724)
-- Dependencies: 236 252 3394
-- Name: fk_mappings_x_entitytypeto; Type: FK CONSTRAINT; Schema: ontology; Owner: postgres
--

ALTER TABLE ONLY mappings
    ADD CONSTRAINT fk_mappings_x_entitytypeto FOREIGN KEY (entitytypeidto) REFERENCES data.entity_types(entitytypeid);


--
-- TOC entry 3452 (class 2606 OID 15704729)
-- Dependencies: 253 3421 243
-- Name: fk_properties_x_rules; Type: FK CONSTRAINT; Schema: ontology; Owner: postgres
--

ALTER TABLE ONLY rules
    ADD CONSTRAINT fk_properties_x_rules FOREIGN KEY (propertyid) REFERENCES properties(propertyid);


--
-- TOC entry 3455 (class 2606 OID 15704734)
-- Dependencies: 252 251 3417
-- Name: fk_relationships_x_relationships_mapping; Type: FK CONSTRAINT; Schema: ontology; Owner: postgres
--

ALTER TABLE ONLY mapping_steps
    ADD CONSTRAINT fk_relationships_x_relationships_mapping FOREIGN KEY (mappingid) REFERENCES mappings(mappingid);


--
-- TOC entry 3456 (class 2606 OID 15704739)
-- Dependencies: 243 251 3407
-- Name: fk_rules_x__mapping_steps; Type: FK CONSTRAINT; Schema: ontology; Owner: postgres
--

ALTER TABLE ONLY mapping_steps
    ADD CONSTRAINT fk_rules_x__mapping_steps FOREIGN KEY (ruleid) REFERENCES rules(ruleid);


-- Completed on 2014-03-20 14:56:50

--
-- PostgreSQL database dump complete
--

-- Add keys for table data.resource_x_resource
--
-- TOC entry 3471 (class 0 OID 0)
-- Dependencies: 240
-- Name: relations_relationid_seq; Type: SEQUENCE OWNED BY; Schema: data; Owner: postgres
--


ALTER TABLE data.resource_x_resource ADD CONSTRAINT "fk_entities_entityid2.rsrc_x_rsrc" FOREIGN KEY ("entityid2") REFERENCES "data"."entities" ("entityid") ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE data.resource_x_resource ADD CONSTRAINT "fk_entities_x_entities1.rsrc_x_rsrc" FOREIGN KEY ("entityid1") REFERENCES "data"."entities" ("entityid") ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE data.resource_x_resource ADD CONSTRAINT "value_x_rsrc_x_rsrc" FOREIGN KEY ("relationshiptype") REFERENCES "concepts"."values" ("valueid") ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.1.4
-- Dumped by pg_dump version 9.1.4
-- Started on 2014-09-10 15:56:10

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

--
-- TOC entry 12 (class 2615 OID 16061322)
-- Name: aux; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA aux;


ALTER SCHEMA aux OWNER TO postgres;

SET search_path = aux, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 256 (class 1259 OID 16061492)
-- Dependencies: 1605 12
-- Name: overlays; Type: TABLE; Schema: aux; Owner: postgres; Tablespace: 
--

CREATE TABLE overlays (
    overlayty text,
    overlayval text,
    geometry public.geometry(Geometry,4326),
    overlayid uuid NOT NULL DEFAULT public.uuid_generate_v1mc()
);


ALTER TABLE aux.overlays OWNER TO postgres;

--
-- TOC entry 3288 (class 2606 OID 16064233)
-- Dependencies: 256 256
-- Name: overlays_pkey; Type: CONSTRAINT; Schema: aux; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY overlays
    ADD CONSTRAINT overlays_pkey PRIMARY KEY (overlayid);


--
-- TOC entry 3289 (class 1259 OID 16064226)
-- Dependencies: 256 2698
-- Name: overlays_sidx; Type: INDEX; Schema: aux; Owner: postgres; Tablespace: 
--

CREATE INDEX overlays_sidx ON overlays USING gist (geometry);


--
-- TOC entry 3290 (class 1259 OID 16064234)
-- Dependencies: 256
-- Name: overlaytype_idx; Type: INDEX; Schema: aux; Owner: postgres; Tablespace: 
--

CREATE INDEX overlaytype_idx ON overlays USING btree (overlayty);


-- Completed on 2014-09-10 15:56:11

--
-- PostgreSQL database dump complete
--
CREATE TABLE aux.addresses
(
  addressid uuid NOT NULL DEFAULT public.uuid_generate_v1mc(),
  addressnum text,
  addressstreet text,
  vintage text,
  geometry public.geometry(MultiPoint,4326),
  city text,
  postalcode text
)
WITH (
  OIDS=FALSE
);
ALTER TABLE aux.addresses
  OWNER TO postgres;

-- Index: aux.addresses_sidx

-- DROP INDEX aux.addresses_sidx;

CREATE INDEX addresses_sidx
  ON aux.addresses
  USING gist
  (geometry );



ALTER TABLE ONLY aux.addresses
    ADD CONSTRAINT addresses_pkey PRIMARY KEY (addressid);



-- Index: aux.addresses_sidx

  -- Table: aux.parcels

-- DROP TABLE aux.parcels;

CREATE TABLE aux.parcels
(
  parcelid uuid NOT NULL DEFAULT public.uuid_generate_v1mc(),
  parcelapn text,
  vintage text,
  geometry public.geometry(MultiPolygon,4326)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE aux.parcels
  OWNER TO postgres;

-- Index: aux.parcels_sidx

-- DROP INDEX aux.parcels_sidx;

CREATE INDEX parcels_sidx
  ON aux.parcels
  USING gist
  (geometry );


ALTER TABLE ONLY aux.parcels
    ADD CONSTRAINT parcels_pkey PRIMARY KEY (parcelid);



CREATE OR REPLACE FUNCTION concepts.concpets_ins()
  RETURNS trigger AS
$BODY$
DECLARE
 v_uuid uuid = public.uuid_generate_v1mc();

BEGIN
--Provides CONCEPTID for RDM inserts and cases where ETL conceptid is not a UUID
  IF NEW.CONCEPTID IS NULL THEN
     NEW.CONCEPTID := v_uuid;
  END IF;

 -- Supports RDM where no concpetid or legacyoid is fed in
  IF NEW.CONCEPTID IS NULL AND (NEW.LEGACYOID IS NULL OR NEW.LEGACYOID = '') THEN
     NEW.LEGACYOID = v_uuid::text;
  END IF;   


-- I would assume that two cases below are handled in python code by being explicit about insert values for both columns... just coding defensively here. ABL.
-- Supports where ETL provided conceptid is a UUID and will be kept, but no LEGACYOID provided.
  IF NEW.CONCEPTID IS NOT NULL and (NEW.LEGACYOID is null or NEW.LEGACYOID = '') THEN
     NEW.LEGACYOID = NEW.CONCEPTID::text;     
  END IF;   

-- Supports where ETL'ed conceptid is not a UUID.  Populates original "concpetid" as LEGACYOID.
  IF NEW.LEGACYOID IS NOT NULL OR NEW.LEGACYOID != '' then
     NEW.LEGACYOID = NEW.LEGACYOID;     
  END IF;   

RETURN NEW;
END$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION concepts.concpets_ins()
  OWNER TO postgres;

  
  
-- Trigger: concepts_ins_tgr on concepts.concepts

-- DROP TRIGGER concepts_ins_tgr ON concepts.concepts;

CREATE TRIGGER concepts_ins_tgr
  BEFORE INSERT
  ON concepts.concepts
  FOR EACH ROW
  EXECUTE PROCEDURE concepts.concpets_ins();
