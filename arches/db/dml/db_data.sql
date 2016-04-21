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
-- Data for Name: d_value_types; Type: TABLE DATA; Schema: concepts; Owner: postgres
--

--SKOS Documentation Properties
INSERT INTO d_value_types VALUES ('scopeNote', 'note', null, 'skos', 'text');
INSERT INTO d_value_types VALUES ('definition', 'note', null, 'skos', 'text');
INSERT INTO d_value_types VALUES ('example', 'note', null, 'skos', 'text');
INSERT INTO d_value_types VALUES ('historyNote', 'note', null, 'skos', 'text');
INSERT INTO d_value_types VALUES ('editorialNote', 'note', null, 'skos', 'text');
INSERT INTO d_value_types VALUES ('changeNote', 'note', null, 'skos', 'text');
INSERT INTO d_value_types VALUES ('note', 'note', null, 'skos');

--SKOS Lexical Properties
INSERT INTO d_value_types VALUES ('prefLabel', 'label', null, 'skos', 'text');
INSERT INTO d_value_types VALUES ('altLabel', 'label', null, 'skos', 'text');
INSERT INTO d_value_types VALUES ('hiddenLabel', 'label', null, 'skos', 'text');

--SKOS Notation (A notation is different from a lexical label in that a notation is not normally recognizable as a word or sequence of words in any natural language. (ie sortorder))
INSERT INTO d_value_types VALUES ('notation', 'notation', null, 'skos', 'text');

--NON-SKOS
INSERT INTO d_value_types VALUES ('image', 'image', null, 'arches', 'text');

--DUBLIN CORE
INSERT INTO d_value_types VALUES ('title', 'label', null, 'dcterms', 'text');
INSERT INTO d_value_types VALUES ('description', 'note', null, 'dcterms', 'text');
INSERT INTO d_value_types VALUES ('collector', 'undefined', null, 'arches', 'text');

--ARCHES PROPERTIES
INSERT INTO d_value_types VALUES ('sortorder', 'undefined', null, 'arches', 'text');

--
-- TOC entry 3329 (class 0 OID 11000965)
-- Dependencies: 226
-- Data for Name: d_relation_types; Type: TABLE DATA; Schema: concepts; Owner: postgres
--

--SKOS Mapping Properties (relationships between concepts across schemes)
INSERT INTO d_relation_types VALUES ('closeMatch', 'Mapping Properties', 'skos');
INSERT INTO d_relation_types VALUES ('mappingRelation', 'Mapping Properties', 'skos');
INSERT INTO d_relation_types VALUES ('narrowMatch', 'Mapping Properties', 'skos');
INSERT INTO d_relation_types VALUES ('relatedMatch', 'Mapping Properties', 'skos');
INSERT INTO d_relation_types VALUES ('broadMatch', 'Mapping Properties', 'skos');
INSERT INTO d_relation_types VALUES ('exactMatch', 'Mapping Properties', 'skos');

--SKOS Semantic Relations (relationship between concepts within a scheme)
INSERT INTO d_relation_types VALUES ('broader', 'Semantic Relations', 'skos');
INSERT INTO d_relation_types VALUES ('broaderTransitive', 'Semantic Relations', 'skos');
INSERT INTO d_relation_types VALUES ('narrower', 'Semantic Relations', 'skos');
INSERT INTO d_relation_types VALUES ('narrowerTransitive', 'Semantic Relations', 'skos');
INSERT INTO d_relation_types VALUES ('related', 'Semantic Relations', 'skos');
INSERT INTO d_relation_types VALUES ('member', 'Concept Collections', 'skos');
INSERT INTO d_relation_types VALUES ('hasTopConcept', 'Properties', 'skos');

--Arches entityttype relations to concepts
INSERT INTO d_relation_types VALUES ('hasCollection', 'Entitytype Relations', 'arches');
INSERT INTO d_relation_types VALUES ('hasEntity', 'Entitynode Relations', 'arches');

--OWL Class types and Arches specific types
INSERT INTO d_node_types VALUES ('GroupingNode', 'arches');
INSERT INTO d_node_types VALUES ('ConceptScheme', 'skos');
INSERT INTO d_node_types VALUES ('Concept', 'skos');
INSERT INTO d_node_types VALUES ('Collection', 'skos');
INSERT INTO d_node_types VALUES ('EntityType', 'arches');


--Data types
INSERT INTO d_data_types VALUES ('string', 'fa fa-file-code-o');
INSERT INTO d_data_types VALUES ('number', 'fa fa-hashtag');
INSERT INTO d_data_types VALUES ('date', 'fa fa-calendar');
INSERT INTO d_data_types VALUES ('geometry', 'fa fa-globe');
INSERT INTO d_data_types VALUES ('domain', 'fa fa-list-ul');
INSERT INTO d_data_types VALUES ('boolean', 'fa fa-toggle-on');
INSERT INTO d_data_types VALUES ('file', 'fa fa-file-image-o');
INSERT INTO d_data_types VALUES ('semantic', 'fa fa-link');


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
    VALUES ('10000000-0000-0000-0000-000000000001', 'string', 'string.htm');

INSERT INTO widgets(widgetid, name, template)
    VALUES ('10000000-0000-0000-0000-000000000002', 'select', 'select.htm');

INSERT INTO widgets(widgetid, name, template)
    VALUES ('10000000-0000-0000-0000-000000000003', 'switch', 'switch.htm');

INSERT INTO widgets(widgetid, name, template)
    VALUES ('10000000-0000-0000-0000-000000000004', 'datepicker', 'datepicker.htm');

-- Node branch
INSERT INTO branch_metadata(graphmetadataid, name, author, version, description)
    VALUES ('22000000-0000-0000-0000-000000000000', 'Node', 'Arches', 'v1', 'Represents a single node in a graph');

INSERT INTO nodes(nodeid, name, description, istopnode, isresource, isactive, ontologyclass, datatype, graphmetadataid)
    VALUES ('20000000-0000-0000-0000-100000000000', 'Node', 'Represents a single node in a graph', 't', 'f', 'f', 'E1', 'string', '22000000-0000-0000-0000-000000000000');

INSERT INTO node_groups(nodegroupid, cardinality, legacygroupid)
    VALUES ('20000000-0000-0000-0000-100000000000', 'n', '');


-- Node/NodeType branch
INSERT INTO branch_metadata(graphmetadataid, name, author, version, description)
    VALUES ('22000000-0000-0000-0000-000000000001', 'Node/Node Type', 'Arches', 'v1', 'Represents a node and node type pairing');

INSERT INTO nodes(nodeid, name, description, istopnode, isresource, isactive, ontologyclass, datatype,
            graphmetadataid, nodegroupid)
    VALUES ('20000000-0000-0000-0000-100000000001', 'Node', '', 't', 'f', 'f', 'E1', 'string',
            '22000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-100000000001');

INSERT INTO nodes(nodeid, name, description, istopnode, isresource, isactive, ontologyclass, datatype,
            graphmetadataid, nodegroupid)
    VALUES ('20000000-0000-0000-0000-100000000002', 'Node Type', '', 'f', 'f', 'f', 'E55', 'domain',
            '22000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-100000000001');

INSERT INTO node_groups(nodegroupid, cardinality, legacygroupid)
    VALUES ('20000000-0000-0000-0000-100000000001', 'n', '');

INSERT INTO edges(domainnodeid, rangenodeid)
    VALUES ('20000000-0000-0000-0000-100000000001', '20000000-0000-0000-0000-100000000002');



INSERT INTO nodes(nodeid, name, description, istopnode, isresource, isactive, ontologyclass, datatype, nodegroupid)
    VALUES ('20000000-0000-0000-0000-000000000000', 'ARCHES_CONFIG', 'Base configuration settings for Arches', 't', 't', 'f', 'E1', 'semantic', '20000000-0000-0000-0000-000000000000');

INSERT INTO nodes(nodeid, name, description, istopnode, isresource, isactive, ontologyclass, datatype,
            nodegroupid)
    VALUES ('20000000-0000-0000-0000-000000000001', 'KEYS', 'Group to hold unique keys used by Arches', 'f', 'f', 'f', 'E1', 'semantic',
            '20000000-0000-0000-0000-000000000001');

INSERT INTO nodes(nodeid, name, description, istopnode, isresource, isactive, ontologyclass, datatype,
            nodegroupid)
    VALUES ('20000000-0000-0000-0000-000000000002', 'KEY_NAME', 'Name of the key', 'f', 'f', 'f', 'E1', 'string',
            '20000000-0000-0000-0000-000000000001');

INSERT INTO nodes(nodeid, name, description, istopnode, isresource, isactive, ontologyclass, datatype,
            nodegroupid)
    VALUES ('20000000-0000-0000-0000-000000000003', 'KEY_TYPE', 'Type of key', 'f', 'f', 'f', 'E55', 'domain',
            '20000000-0000-0000-0000-000000000001');

INSERT INTO nodes(nodeid, name, description, istopnode, isresource, isactive, ontologyclass, datatype,
            nodegroupid)
    VALUES ('20000000-0000-0000-0000-000000000004', 'KEY_VALUE', 'Value of the key', 'f', 'f', 'f', 'E1', 'string',
            '20000000-0000-0000-0000-000000000001');

INSERT INTO edges(domainnodeid, rangenodeid)
    VALUES ('20000000-0000-0000-0000-000000000000', '20000000-0000-0000-0000-000000000001');

INSERT INTO edges(domainnodeid, rangenodeid)
    VALUES ('20000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000002');

INSERT INTO edges(domainnodeid, rangenodeid)
    VALUES ('20000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000003');

INSERT INTO edges(domainnodeid, rangenodeid)
    VALUES ('20000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000004');

INSERT INTO node_groups(nodegroupid, cardinality, legacygroupid)
    VALUES ('20000000-0000-0000-0000-000000000000', 'n', '');

INSERT INTO node_groups(nodegroupid, cardinality, legacygroupid)
    VALUES ('20000000-0000-0000-0000-000000000001', 'n', '');

INSERT INTO node_groups(nodegroupid, cardinality, legacygroupid)
    VALUES ('99999999-0000-0000-0000-000000000001', 'n', '');

INSERT INTO node_groups(nodegroupid, cardinality, legacygroupid)
    VALUES ('32999999-0000-0000-0000-000000000000', 'n', '');

INSERT INTO node_groups(nodegroupid, cardinality, legacygroupid)
    VALUES ('19999999-0000-0000-0000-000000000000', 'n', '');

INSERT INTO node_groups(nodegroupid, cardinality, legacygroupid)
    VALUES ('21111111-0000-0000-0000-000000000000', '1', '');

INSERT INTO node_groups(nodegroupid, cardinality, legacygroupid)
    VALUES ('11111111-0000-0000-0000-000000000000', 'n', '');

INSERT INTO cards(cardid, name, title, subtitle)
    VALUES ('30000000-0000-0000-0000-000000000000', 'Keys', 'Keys', '');

INSERT INTO cards(cardid, name, title, subtitle)
    VALUES ('50000000-0000-0000-0000-000000000000', 'test card group', 'A card group title', '');

INSERT INTO resource_instances(resourceinstanceid, resourceclassid)
    VALUES ('40000000-0000-0000-0000-000000000000','20000000-0000-0000-0000-000000000004');

INSERT INTO validations(validationid, validation, validationtype, name, description)
    VALUES ('60000000-0000-0000-0000-000000000000', 'required', 'node', 'required', 'A value must be entered for this node.');

INSERT INTO validations_x_nodes(validation_id, node_id)
    VALUES ('60000000-0000-0000-0000-000000000000', '20000000-0000-0000-0000-000000000004');


-- INSERT INTO tile_instances(tileinstanceid, tilegroupid, tileinstancedata, cardid,
--             resourceclassid, resourceinstanceid)
--     VALUES ('40000000-0000-0000-0000-000000000000', '', '{
--                 "20000000-0000-0000-0000-000000000003": "1",
--                 "20000000-0000-0000-0000-000000000002": "Map Key",
--                 "20000000-0000-0000-0000-000000000004": "23984ll2399494"
--             }', '30000000-0000-0000-0000-000000000000',
--             '20000000-0000-0000-0000-000000000000', '40000000-0000-0000-0000-000000000000');
