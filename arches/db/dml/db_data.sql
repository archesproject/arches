--
-- PostgreSQL database dump
--

-- Dumped from database version 9.1.4
-- Dumped by pg_dump version 9.1.4
-- Started on 2013-06-25 15:32:29

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
--SET standard_conformi= on;
SET check_function_bodies = false;
SET client_min_messages = warning;



--
-- TOC entry 3327 (class 0 OID 11000953)
-- Dependencies: 224
-- Data for Name: d_languages; Type: TABLE DATA; Schema: concepts; Owner: postgres
--

INSERT INTO d_languages VALUES ('en-US', 'ENGLISH', true);


--
-- TOC entry 3328 (class 0 OID 11000959)
-- Dependencies: 225
-- Data for Name: d_valuetypes; Type: TABLE DATA; Schema: concepts; Owner: postgres
--

--SKOS Documentation Properties
INSERT INTO d_valuetypes VALUES ('scopeNote', 'note', null, 'skos', 'text');
INSERT INTO d_valuetypes VALUES ('definition', 'note', null, 'skos', 'text');
INSERT INTO d_valuetypes VALUES ('example', 'note', null, 'skos', 'text');
INSERT INTO d_valuetypes VALUES ('historyNote', 'note', null, 'skos', 'text');
INSERT INTO d_valuetypes VALUES ('editorialNote', 'note', null, 'skos', 'text');
INSERT INTO d_valuetypes VALUES ('changeNote', 'note', null, 'skos', 'text');
INSERT INTO d_valuetypes VALUES ('note', 'note', null, 'skos');

--SKOS Lexical Properties
INSERT INTO d_valuetypes VALUES ('prefLabel', 'label', null, 'skos', 'text');
INSERT INTO d_valuetypes VALUES ('altLabel', 'label', null, 'skos', 'text');
INSERT INTO d_valuetypes VALUES ('hiddenLabel', 'label', null, 'skos', 'text');

--SKOS Notation (A notation is different from a lexical label in that a notation is not normally recognizable as a word or sequence of words in any natural language. (ie sortorder))
INSERT INTO d_valuetypes VALUES ('notation', 'notation', null, 'skos', 'text');

--NON-SKOS
INSERT INTO d_valuetypes VALUES ('image', 'image', null, 'arches', 'text');

--DUBLIN CORE
INSERT INTO d_valuetypes VALUES ('title', 'label', null, 'dcterms', 'text');
INSERT INTO d_valuetypes VALUES ('description', 'note', null, 'dcterms', 'text');
INSERT INTO d_valuetypes VALUES ('collector', 'undefined', null, 'arches', 'text');

--ARCHES PROPERTIES
INSERT INTO d_valuetypes VALUES ('sortorder', 'undefined', null, 'arches', 'text');

--
-- TOC entry 3329 (class 0 OID 11000965)
-- Dependencies: 226
-- Data for Name: d_relationtypes; Type: TABLE DATA; Schema: concepts; Owner: postgres
--

--SKOS Mapping Properties (relationships between concepts across schemes)
INSERT INTO d_relationtypes VALUES ('closeMatch', 'Mapping Properties', 'skos');
INSERT INTO d_relationtypes VALUES ('mappingRelation', 'Mapping Properties', 'skos');
INSERT INTO d_relationtypes VALUES ('narrowMatch', 'Mapping Properties', 'skos');
INSERT INTO d_relationtypes VALUES ('relatedMatch', 'Mapping Properties', 'skos');
INSERT INTO d_relationtypes VALUES ('broadMatch', 'Mapping Properties', 'skos');
INSERT INTO d_relationtypes VALUES ('exactMatch', 'Mapping Properties', 'skos');

--SKOS Semantic Relations (relationship between concepts within a scheme)
INSERT INTO d_relationtypes VALUES ('broader', 'Semantic Relations', 'skos');
INSERT INTO d_relationtypes VALUES ('broaderTransitive', 'Semantic Relations', 'skos');
INSERT INTO d_relationtypes VALUES ('narrower', 'Semantic Relations', 'skos');
INSERT INTO d_relationtypes VALUES ('narrowerTransitive', 'Semantic Relations', 'skos');
INSERT INTO d_relationtypes VALUES ('related', 'Semantic Relations', 'skos');
INSERT INTO d_relationtypes VALUES ('member', 'Concept Collections', 'skos');
INSERT INTO d_relationtypes VALUES ('hasTopConcept', 'Properties', 'skos');

--Arches entityttype relations to concepts
INSERT INTO d_relationtypes VALUES ('hasCollection', 'Entitytype Relations', 'arches');
INSERT INTO d_relationtypes VALUES ('hasEntity', 'Entitynode Relations', 'arches');

--OWL Class types and Arches specific types
INSERT INTO d_nodetypes VALUES ('GroupingNode', 'arches');
INSERT INTO d_nodetypes VALUES ('ConceptScheme', 'skos');
INSERT INTO d_nodetypes VALUES ('Concept', 'skos');
INSERT INTO d_nodetypes VALUES ('Collection', 'skos');
INSERT INTO d_nodetypes VALUES ('EntityType', 'arches');



INSERT INTO concepts(conceptid, nodetype, legacyoid) VALUES ('00000000-0000-0000-0000-000000000001', 'ConceptScheme', 'ARCHES');
INSERT INTO concepts(conceptid, nodetype, legacyoid) VALUES ('00000000-0000-0000-0000-000000000003', 'GroupingNode', 'DROPDOWNS');
INSERT INTO concepts(conceptid, nodetype, legacyoid) VALUES ('00000000-0000-0000-0000-000000000004', 'GroupingNode', 'ENTITY NODES');
INSERT INTO concepts(conceptid, nodetype, legacyoid) VALUES ('00000000-0000-0000-0000-000000000005', 'Collection', 'ARCHES RESOURCE CROSS-REFERENCE RELATIONSHIP TYPES.E32.csv');
INSERT INTO concepts(conceptid, nodetype, legacyoid) VALUES ('00000000-0000-0000-0000-000000000006', 'ConceptScheme', 'CANDIDATES');


INSERT INTO relations(relationid, conceptidfrom, conceptidto, relationtype) VALUES (public.uuid_generate_v1mc(), '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000005', 'hasTopConcept');

INSERT INTO values(valueid, conceptid, valuetype, value, languageid) VALUES (public.uuid_generate_v1mc(), '00000000-0000-0000-0000-000000000001', 'prefLabel', 'Arches', 'en-US');
INSERT INTO values(valueid, conceptid, valuetype, value, languageid) VALUES (public.uuid_generate_v1mc(), '00000000-0000-0000-0000-000000000003', 'prefLabel', 'Dropdown Lists', 'en-US');
INSERT INTO values(valueid, conceptid, valuetype, value, languageid) VALUES (public.uuid_generate_v1mc(), '00000000-0000-0000-0000-000000000004', 'prefLabel', 'Entity Nodes', 'en-US');
INSERT INTO values(valueid, conceptid, valuetype, value, languageid) VALUES (public.uuid_generate_v1mc(), '00000000-0000-0000-0000-000000000005', 'prefLabel', 'Resource To Resource Relationship Types', 'en-US');
INSERT INTO values(valueid, conceptid, valuetype, value, languageid) VALUES (public.uuid_generate_v1mc(), '00000000-0000-0000-0000-000000000006', 'prefLabel', 'Candidates', 'en-US');


-- INSERT INTO entity_types(classid, conceptid, businesstablename, publishbydefault, entitytypeid, isresource)
--     VALUES ('E55', '00000000-0000-0000-0000-000000000005', 'domains', false, 'ARCHES_RESOURCE_CROSS-REFERENCE_RELATIONSHIP_TYPES.E55', false);

INSERT INTO relations(relationid, conceptidfrom, conceptidto, relationtype)
    VALUES (public.uuid_generate_v1mc(), '00000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000005', 'hasCollection');

SET search_path = public, pg_catalog;

INSERT INTO auth_user(username, first_name, last_name, email, password, is_staff, is_active, is_superuser, last_login, date_joined)
    VALUES ('admin', '', '', '', 'pbkdf2_sha256$24000$NjdJsyUb6vMd$YM3B8ImPgpF4Mr+jBSFnKu+P5jNmxD/mqwxQUXaLLmI=', 't', 't', 't', '2012-03-15 15:29:31.211-07', '2012-03-15 15:29:31.211-07');

INSERT INTO auth_user(username, first_name, last_name, email, password, is_staff, is_active, is_superuser, last_login, date_joined)
    VALUES ('anonymous', '', '', '', '!S9npj7MhUqm30gT5ldm4TposL8jU5jDL4Ab02uuK', 'f', 't', 'f', '2012-03-15 15:29:31.211-07', '2012-03-15 15:29:31.211-07');

INSERT INTO widgets(widgetid, name, template)
    VALUES ('10000000-0000-0000-0000-000000000001', 'string', 'app/templates/views/forms/widgets/string.htm');

INSERT INTO widgets(widgetid, name, template)
    VALUES ('10000000-0000-0000-0000-000000000002', 'select', 'app/templates/views/forms/widgets/select.htm');