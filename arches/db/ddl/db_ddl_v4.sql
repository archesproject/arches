
CREATE FUNCTION concepts.get_conceptid(p_label text) RETURNS uuid
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
-- TOC entry 1266 (class 1255 OID 15704207)
-- Dependencies: 9 1863
-- Name: insert_concept(text, text, text, text, text); Type: FUNCTION; Schema: concepts; Owner: postgres
--

CREATE FUNCTION concepts.insert_concept(p_label text, p_note text, p_languageid text, p_legacyid text, p_nodetype text) RETURNS uuid
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

CREATE FUNCTION concepts.insert_relation(p_legacyid1 text, p_relationtype text, p_legacyid2 text) RETURNS text
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


CREATE FUNCTION ontology.insert_mappings(p_mapping text, p_mergenodeid text) RETURNS integer
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

CREATE FUNCTION ontology.insert_mapping_step(p_mappingid text, p_domain text, p_property text, p_range text, p_entitytypefrom text, p_entitytypeto text, p_order integer) RETURNS text
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

CREATE FUNCTION ontology.insert_mapping(p_entityfrom text, p_entityto text, p_mergenodeid text) RETURNS text
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

CREATE FUNCTION ontology.insert_rule(p_domain text, p_property text, p_range text) RETURNS text
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
-- TOC entry 1282 (class 1255 OID 15704223)
-- Dependencies: 1863 10
-- Name: insert_entitytype(text, text, boolean, text, text, text, text, text, text, text, text); Type: FUNCTION; Schema: data; Owner: postgres
--

CREATE FUNCTION data.insert_entitytype(p_entitytypeid text, p_businesstablename text, p_publishbydefault boolean, p_icon text, p_defaultvectorcolor text, p_asset_entity text, p_note text, p_notelanguage text, p_entitynamelanguage text, p_entitynametype text, p_parentconceptlabel text) RETURNS text
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