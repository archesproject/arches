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


SET search_path = concepts, pg_catalog;

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


INSERT INTO relations(conceptidfrom, conceptidto, relationtype) VALUES ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000005', 'hasTopConcept');

INSERT INTO values(conceptid, valuetype, value, languageid) VALUES ('00000000-0000-0000-0000-000000000001', 'prefLabel', 'Arches', 'en-US');
INSERT INTO values(conceptid, valuetype, value, languageid) VALUES ('00000000-0000-0000-0000-000000000003', 'prefLabel', 'Dropdown Lists', 'en-US');
INSERT INTO values(conceptid, valuetype, value, languageid) VALUES ('00000000-0000-0000-0000-000000000004', 'prefLabel', 'Entity Nodes', 'en-US');
INSERT INTO values(conceptid, valuetype, value, languageid) VALUES ('00000000-0000-0000-0000-000000000005', 'prefLabel', 'Resource To Resource Relationship Types', 'en-US');
INSERT INTO values(conceptid, valuetype, value, languageid) VALUES ('00000000-0000-0000-0000-000000000006', 'prefLabel', 'Candidates', 'en-US');


SET search_path = ontology, pg_catalog;


INSERT INTO classes VALUES ('E10', 'Transfer of Custody', true);
INSERT INTO classes VALUES ('E11', 'Modification', true);
INSERT INTO classes VALUES ('E16', 'Measurement', true);
INSERT INTO classes VALUES ('E19', 'Physical Object', true);
INSERT INTO classes VALUES ('E2', 'Temporal Entity', true);
INSERT INTO classes VALUES ('E20', 'Biological Object', true);
INSERT INTO classes VALUES ('E22', 'Man-Made Object', true);
INSERT INTO classes VALUES ('E24', 'Physical Man-Made Thing', true);
INSERT INTO classes VALUES ('E25', 'Man-Made Feature', true);
INSERT INTO classes VALUES ('E26', 'Physical Feature', true);
INSERT INTO classes VALUES ('E28', 'Conceptual Object', true);
INSERT INTO classes VALUES ('E33', 'Linguistic Object', true);
INSERT INTO classes VALUES ('E35', 'Title', true);
INSERT INTO classes VALUES ('E36', 'Visual Item', true);
INSERT INTO classes VALUES ('E37', 'Mark', true);
INSERT INTO classes VALUES ('E40', 'Legal Body', true);
INSERT INTO classes VALUES ('E46', 'Section Definition', true);
INSERT INTO classes VALUES ('E51', 'Contact Point', true);
INSERT INTO classes VALUES ('E56', 'Language', true);
INSERT INTO classes VALUES ('E59', 'Primitive Value', true);
INSERT INTO classes VALUES ('E6', 'Destruction', true);
INSERT INTO classes VALUES ('E61', 'Time Primitive', true);
INSERT INTO classes VALUES ('E63', 'Beginning of Existence', true);
INSERT INTO classes VALUES ('E64', 'End of Existence', true);
INSERT INTO classes VALUES ('E66', 'Formation', true);
INSERT INTO classes VALUES ('E68', 'Dissolution', true);
INSERT INTO classes VALUES ('E70', 'Thing', true);
INSERT INTO classes VALUES ('E71', 'Man-Made Thing', true);
INSERT INTO classes VALUES ('E72', 'Legal Object', true);
INSERT INTO classes VALUES ('E73', 'Information Object', true);
INSERT INTO classes VALUES ('E75', 'Conceptual Object Appellation', true);
INSERT INTO classes VALUES ('E77', 'Persistent Item', true);
INSERT INTO classes VALUES ('E78', 'Collection', true);
INSERT INTO classes VALUES ('E79', 'Part Addition', true);
INSERT INTO classes VALUES ('E8', 'Acquisition Event', true);
INSERT INTO classes VALUES ('E80', 'Part Removal', true);
INSERT INTO classes VALUES ('E81', 'Transformation', true);
INSERT INTO classes VALUES ('E83', 'Type Creation', true);
INSERT INTO classes VALUES ('E84', 'Information Carrier', true);
INSERT INTO classes VALUES ('E85', 'Joining', true);
INSERT INTO classes VALUES ('E86', 'Leaving', true);
INSERT INTO classes VALUES ('E87', 'Curation Activity', true);
INSERT INTO classes VALUES ('E89', 'Propositional Object', true);
INSERT INTO classes VALUES ('E9', 'Move', true);
INSERT INTO classes VALUES ('E90', 'Symbolic Object', true);
INSERT INTO classes VALUES ('E1', 'CRM Entity', true);
INSERT INTO classes VALUES ('E12', 'Production', true);
INSERT INTO classes VALUES ('E13', 'Attribute Assignment', true);
INSERT INTO classes VALUES ('E14', 'Condition Assessment', true);
INSERT INTO classes VALUES ('E15', 'Identifier Assignment', true);
INSERT INTO classes VALUES ('E17', 'Type Assignment', true);
INSERT INTO classes VALUES ('E18', 'Physical Thing', true);
INSERT INTO classes VALUES ('E21', 'Person', true);
INSERT INTO classes VALUES ('E27', 'Site', true);
INSERT INTO classes VALUES ('E29', 'Design or Procedure', true);
INSERT INTO classes VALUES ('E3', 'Condition State', true);
INSERT INTO classes VALUES ('E30', 'Right', true);
INSERT INTO classes VALUES ('E31', 'Document', true);
INSERT INTO classes VALUES ('E32', 'Authority Document', true);
INSERT INTO classes VALUES ('E34', 'Inscription', true);
INSERT INTO classes VALUES ('E38', 'Image', true);
INSERT INTO classes VALUES ('E39', 'Actor', true);
INSERT INTO classes VALUES ('E4', 'Period', true);
INSERT INTO classes VALUES ('E41', 'Appellation', true);
INSERT INTO classes VALUES ('E42', 'Identifier', true);
INSERT INTO classes VALUES ('E44', 'Place Appellation', true);
INSERT INTO classes VALUES ('E45', 'Address', true);
INSERT INTO classes VALUES ('E47', 'Spatial Coordinates', true);
INSERT INTO classes VALUES ('E48', 'Place Name', true);
INSERT INTO classes VALUES ('E49', 'Time Appellation', true);
INSERT INTO classes VALUES ('E5', 'Event', true);
INSERT INTO classes VALUES ('E50', 'Date', true);
INSERT INTO classes VALUES ('E52', 'Time-Span', true);
INSERT INTO classes VALUES ('E53', 'Place', true);
INSERT INTO classes VALUES ('E54', 'Dimension', true);
INSERT INTO classes VALUES ('E55', 'Type', true);
INSERT INTO classes VALUES ('E57', 'Material', true);
INSERT INTO classes VALUES ('E58', 'Measurement Unit', true);
INSERT INTO classes VALUES ('E60', 'Number', true);
INSERT INTO classes VALUES ('E62', 'String', true);
INSERT INTO classes VALUES ('E65', 'Creation', true);
INSERT INTO classes VALUES ('E67', 'Birth', true);
INSERT INTO classes VALUES ('E69', 'Death', true);
INSERT INTO classes VALUES ('E7', 'Activity', true);
INSERT INTO classes VALUES ('E74', 'Group', true);
INSERT INTO classes VALUES ('E82', 'Actor Appellation', true);


--
-- TOC entry 3332 (class 0 OID 11001159)
-- Dependencies: 261 3331 3331
-- Data for Name: properties; Type: TABLE DATA; Schema: ontology; Owner: postgres
--

INSERT INTO properties VALUES ('-P25', 'E19', 'E9',NULL);
INSERT INTO properties VALUES ('P10', 'E4', 'E4','falls within');
INSERT INTO properties VALUES ('-P10', 'E4', 'E4','contains');
INSERT INTO properties VALUES ('P100', 'E69', 'E21','was death of');
INSERT INTO properties VALUES ('-P100', 'E21', 'E69','died in');
INSERT INTO properties VALUES ('-P101', 'E55', 'E70','was use of');
INSERT INTO properties VALUES ('P102', 'E71', 'E35','has title');
INSERT INTO properties VALUES ('-P102', 'E35', 'E71','is title of');
INSERT INTO properties VALUES ('-P103', 'E55', 'E71','was intention of');
INSERT INTO properties VALUES ('P104', 'E72', 'E30','is subject to');
INSERT INTO properties VALUES ('-P104', 'E30', 'E72','applies to');
INSERT INTO properties VALUES ('-P105', 'E39', 'E72','has right on');
INSERT INTO properties VALUES ('P106', 'E90', 'E90','is composed of');
INSERT INTO properties VALUES ('-P106', 'E90', 'E90','forms part of');
INSERT INTO properties VALUES ('-P107', 'E39', 'E74','is current or former member of');
INSERT INTO properties VALUES ('P108', 'E12', 'E24','has produced');
INSERT INTO properties VALUES ('P109', 'E78', 'E39','has current or former curator');
INSERT INTO properties VALUES ('P11', 'E5', 'E39','had participant');
INSERT INTO properties VALUES ('-P11', 'E39', 'E5','participated in');
INSERT INTO properties VALUES ('P110', 'E79', 'E24','augmented');
INSERT INTO properties VALUES ('-P110', 'E24', 'E79','was augmented by');
INSERT INTO properties VALUES ('-P111', 'E18', 'E79','was added by');
INSERT INTO properties VALUES ('P112', 'E80', 'E24','diminished');
INSERT INTO properties VALUES ('P113', 'E80', 'E18','removed');
INSERT INTO properties VALUES ('-P113', 'E18', 'E80','was removed by');
INSERT INTO properties VALUES ('P114', 'E2', 'E2','is equal in time to');
INSERT INTO properties VALUES ('P115', 'E2', 'E2','finishes');
INSERT INTO properties VALUES ('P116', 'E2', 'E2','starts');
INSERT INTO properties VALUES ('-P116', 'E2', 'E2','is started by');
INSERT INTO properties VALUES ('P117', 'E2', 'E2','occurs during');
INSERT INTO properties VALUES ('-P117', 'E2', 'E2','includes');
INSERT INTO properties VALUES ('-P118', 'E2', 'E2','is overlapped in time by');
INSERT INTO properties VALUES ('P119', 'E2', 'E2','meets in time with');
INSERT INTO properties VALUES ('P12', 'E5', 'E77','occurred in the presence of');
INSERT INTO properties VALUES ('-P12', 'E77', 'E5','was present at');
INSERT INTO properties VALUES ('P120', 'E2', 'E2','occurs  before');
INSERT INTO properties VALUES ('P121', 'E53', 'E53','overlaps with');
INSERT INTO properties VALUES ('P122', 'E53', 'E53','borders with');
INSERT INTO properties VALUES ('P123', 'E81', 'E77','resulted in');
INSERT INTO properties VALUES ('P124', 'E81', 'E77','transformed');
INSERT INTO properties VALUES ('-P124', 'E77', 'E81','was transformed by');
INSERT INTO properties VALUES ('-P125', 'E55', 'E7','was type of object used in');
INSERT INTO properties VALUES ('P126', 'E11', 'E57','employed');
INSERT INTO properties VALUES ('P127', 'E55', 'E55','has broader term');
INSERT INTO properties VALUES ('-P127', 'E55', 'E55','has narrower term');
INSERT INTO properties VALUES ('P128', 'E24', 'E73','carries');
INSERT INTO properties VALUES ('P129', 'E89', 'E1','is about');
INSERT INTO properties VALUES ('-P129', 'E1', 'E89','is subject of');
INSERT INTO properties VALUES ('P13', 'E6', 'E18','destroyed');
INSERT INTO properties VALUES ('-P13', 'E18', 'E6','was destroyed by');
INSERT INTO properties VALUES ('-P130', 'E70', 'E70','features are also found on');
INSERT INTO properties VALUES ('P131', 'E39', 'E82','is identified by');
INSERT INTO properties VALUES ('P132', 'E4', 'E4','overlaps with');
INSERT INTO properties VALUES ('P133', 'E4', 'E4','is separated from');
INSERT INTO properties VALUES ('P134', 'E7', 'E7','continued');
INSERT INTO properties VALUES ('P135', 'E83', 'E55','created type');
INSERT INTO properties VALUES ('-P135', 'E55', 'E83','was created by');
INSERT INTO properties VALUES ('P136', 'E83', 'E1','was based on');
INSERT INTO properties VALUES ('P137', 'E1', 'E55','exemplifies');
INSERT INTO properties VALUES ('-P137', 'E55', 'E1','is exemplified by');
INSERT INTO properties VALUES ('P138', 'E36', 'E1','represents');
INSERT INTO properties VALUES ('P139', 'E41', 'E41','has alternative form');
INSERT INTO properties VALUES ('P14', 'E7', 'E39','carried out by');
INSERT INTO properties VALUES ('-P14', 'E39', 'E7','performed');
INSERT INTO properties VALUES ('-P140', 'E1', 'E13','was attributed by');
INSERT INTO properties VALUES ('P141', 'E13', 'E1','assigned');
INSERT INTO properties VALUES ('-P141', 'E1', 'E13','was assigned by');
INSERT INTO properties VALUES ('-P142', 'E41', 'E15','was used in');
INSERT INTO properties VALUES ('P143', 'E85', 'E39','joined');
INSERT INTO properties VALUES ('-P143', 'E39', 'E85','was joined by');
INSERT INTO properties VALUES ('-P144', 'E74', 'E85','gained member by');
INSERT INTO properties VALUES ('P145', 'E86', 'E39','separated');
INSERT INTO properties VALUES ('-P145', 'E39', 'E86','left by');
INSERT INTO properties VALUES ('P146', 'E86', 'E74','separated from');
INSERT INTO properties VALUES ('P147', 'E87', 'E78','curated');
INSERT INTO properties VALUES ('-P147', 'E78', 'E87','was curated by');
INSERT INTO properties VALUES ('P148', 'E89', 'E89','has component');
INSERT INTO properties VALUES ('P15', 'E7', 'E1','was influenced by');
INSERT INTO properties VALUES ('-P15', 'E1', 'E7','influenced');
INSERT INTO properties VALUES ('P16', 'E7', 'E70','used specific object');
INSERT INTO properties VALUES ('P17', 'E7', 'E1','was  motivated by');
INSERT INTO properties VALUES ('-P17', 'E1', 'E7','motivated');
INSERT INTO properties VALUES ('P19', 'E7', 'E71','was intended use of');
INSERT INTO properties VALUES ('P2', 'E1', 'E55','has type');
INSERT INTO properties VALUES ('-P2', 'E55', 'E1','is type of');
INSERT INTO properties VALUES ('P20', 'E7', 'E5','had specific purpose');
INSERT INTO properties VALUES ('-P20', 'E5', 'E7','was purpose of');
INSERT INTO properties VALUES ('-P21', 'E55', 'E7','was purpose of');
INSERT INTO properties VALUES ('P22', 'E8', 'E39','transferred title to');
INSERT INTO properties VALUES ('P23', 'E8', 'E39','transferred title from');
INSERT INTO properties VALUES ('-P23', 'E39', 'E8','surrendered title through');
INSERT INTO properties VALUES ('-P24', 'E18', 'E8','changed ownership through');
INSERT INTO properties VALUES ('P25', 'E9', 'E19','moved');
INSERT INTO properties VALUES ('P26', 'E9', 'E53','moved to');
INSERT INTO properties VALUES ('P27', 'E9', 'E53','moved from');
INSERT INTO properties VALUES ('-P27', 'E53', 'E9','was origin of');
INSERT INTO properties VALUES ('P28', 'E10', 'E39','custody surrendered by');
INSERT INTO properties VALUES ('P29', 'E10', 'E39','custody received by');
INSERT INTO properties VALUES ('-P29', 'E39', 'E10','received custody through');
INSERT INTO properties VALUES ('P30', 'E10', 'E18','transferred custody of');
INSERT INTO properties VALUES ('P33', 'E7', 'E29',NULL);
INSERT INTO properties VALUES ('-P43', 'E54', 'E70',NULL);
INSERT INTO properties VALUES ('P62', 'E24', 'E1',NULL);
INSERT INTO properties VALUES ('-P62', 'E1', 'E24',NULL);
INSERT INTO properties VALUES ('P1', 'E1', 'E41','is identified by');
INSERT INTO properties VALUES ('-P1', 'E41', 'E1','identifies');
INSERT INTO properties VALUES ('P101', 'E70', 'E55','had as general use');
INSERT INTO properties VALUES ('P103', 'E71', 'E55','was intended for');
INSERT INTO properties VALUES ('P105', 'E72', 'E39','right held by');
INSERT INTO properties VALUES ('P107', 'E74', 'E39','has current or former member');
INSERT INTO properties VALUES ('-P108', 'E24', 'E12','was produced by');
INSERT INTO properties VALUES ('-P109', 'E39', 'E78','is current or former curator of');
INSERT INTO properties VALUES ('P111', 'E79', 'E18','added');
INSERT INTO properties VALUES ('P31', 'E11', 'E24','has modified');
INSERT INTO properties VALUES ('P32', 'E7', 'E55','used general technique');
INSERT INTO properties VALUES ('-P32', 'E55', 'E7','was technique of');
INSERT INTO properties VALUES ('P34', 'E14', 'E18','concerned');
INSERT INTO properties VALUES ('-P34', 'E18', 'E14','was assessed by');
INSERT INTO properties VALUES ('P35', 'E14', 'E3','has identified');
INSERT INTO properties VALUES ('P37', 'E15', 'E42','assigned');
INSERT INTO properties VALUES ('-P37', 'E42', 'E15','was assigned by');
INSERT INTO properties VALUES ('P38', 'E15', 'E42','deassigned');
INSERT INTO properties VALUES ('-P38', 'E42', 'E15','was deassigned by');
INSERT INTO properties VALUES ('-P39', 'E1', 'E16','was measured by');
INSERT INTO properties VALUES ('P4', 'E2', 'E52','has time-span');
INSERT INTO properties VALUES ('-P4', 'E52', 'E2','is time-span of');
INSERT INTO properties VALUES ('-P40', 'E54', 'E16','was observed in');
INSERT INTO properties VALUES ('P41', 'E17', 'E1','classified');
INSERT INTO properties VALUES ('-P41', 'E1', 'E17','was classified by');
INSERT INTO properties VALUES ('-P42', 'E55', 'E17','was assigned by');
INSERT INTO properties VALUES ('P43', 'E70', 'E54','has dimension');
INSERT INTO properties VALUES ('P44', 'E18', 'E3','has condition');
INSERT INTO properties VALUES ('P45', 'E18', 'E57','consists of');
INSERT INTO properties VALUES ('-P45', 'E57', 'E18','is incorporated in');
INSERT INTO properties VALUES ('-P46', 'E18', 'E18','forms part of');
INSERT INTO properties VALUES ('P48', 'E1', 'E42','has preferred identifier');
INSERT INTO properties VALUES ('P49', 'E18', 'E39','has former or current keeper');
INSERT INTO properties VALUES ('-P49', 'E39', 'E18','is former or current keeper of');
INSERT INTO properties VALUES ('-P5', 'E3', 'E3','forms part of');
INSERT INTO properties VALUES ('P50', 'E18', 'E39','has current keeper');
INSERT INTO properties VALUES ('P51', 'E18', 'E39','has former or current owner');
INSERT INTO properties VALUES ('-P51', 'E39', 'E18','is former or current owner of');
INSERT INTO properties VALUES ('-P52', 'E39', 'E18','is current owner of');
INSERT INTO properties VALUES ('-P53', 'E53', 'E18','is former or current location of');
INSERT INTO properties VALUES ('P54', 'E19', 'E53','has current permanent location');
INSERT INTO properties VALUES ('P55', 'E19', 'E53','has current location');
INSERT INTO properties VALUES ('-P55', 'E53', 'E19','currently holds');
INSERT INTO properties VALUES ('P56', 'E19', 'E26','bears feature');
INSERT INTO properties VALUES ('P57', 'E19', 'E60','has number of parts');
INSERT INTO properties VALUES ('P58', 'E18', 'E46','has section definition');
INSERT INTO properties VALUES ('P59', 'E18', 'E53','has section');
INSERT INTO properties VALUES ('-P59', 'E53', 'E18','is located on or within');
INSERT INTO properties VALUES ('-P65', 'E36', 'E24','is shown by');
INSERT INTO properties VALUES ('P67', 'E89', 'E1','refers to');
INSERT INTO properties VALUES ('-P67', 'E1', 'E89','is referred to by');
INSERT INTO properties VALUES ('-P68', 'E57', 'E29','use foreseen by');
INSERT INTO properties VALUES ('P69', 'E29', 'E29','is associated with');
INSERT INTO properties VALUES ('P7', 'E4', 'E53','took place at');
INSERT INTO properties VALUES ('P70', 'E31', 'E1','documents');
INSERT INTO properties VALUES ('-P70', 'E1', 'E31','is documented in');
INSERT INTO properties VALUES ('P71', 'E32', 'E55','lists');
INSERT INTO properties VALUES ('-P71', 'E55', 'E32','is listed in');
INSERT INTO properties VALUES ('-P72', 'E56', 'E33','is language of');
INSERT INTO properties VALUES ('P73', 'E33', 'E33','has translation');
INSERT INTO properties VALUES ('P74', 'E39', 'E53','has current or former residence');
INSERT INTO properties VALUES ('-P74', 'E53', 'E39','is current or former residence of');
INSERT INTO properties VALUES ('-P75', 'E30', 'E39','is possessed by');
INSERT INTO properties VALUES ('P76', 'E39', 'E51','has contact point');
INSERT INTO properties VALUES ('P78', 'E52', 'E49','is identified by');
INSERT INTO properties VALUES ('-P78', 'E49', 'E52','identifies');
INSERT INTO properties VALUES ('P79', 'E52', 'E62','beginning is qualified by');
INSERT INTO properties VALUES ('-P8', 'E19', 'E4','witnessed');
INSERT INTO properties VALUES ('P80', 'E52', 'E62','end is qualified by');
INSERT INTO properties VALUES ('P81', 'E52', 'E61','ongoing throughout');
INSERT INTO properties VALUES ('P83', 'E52', 'E54','had at least duration');
INSERT INTO properties VALUES ('-P83', 'E54', 'E52','was minimum duration of');
INSERT INTO properties VALUES ('-P84', 'E54', 'E52','was maximum duration of');
INSERT INTO properties VALUES ('P86', 'E52', 'E52','falls within');
INSERT INTO properties VALUES ('P87', 'E53', 'E44','is identified by');
INSERT INTO properties VALUES ('-P87', 'E44', 'E53','identifies');
INSERT INTO properties VALUES ('P88', 'E53', 'E53','consists of');
INSERT INTO properties VALUES ('P89', 'E53', 'E53','falls within');
INSERT INTO properties VALUES ('-P89', 'E53', 'E53','contains');
INSERT INTO properties VALUES ('P9', 'E4', 'E4','consists of');
INSERT INTO properties VALUES ('P90', 'E54', 'E60','has value');
INSERT INTO properties VALUES ('P91', 'E54', 'E58','has unit');
INSERT INTO properties VALUES ('-P91', 'E58', 'E54','is unit of');
INSERT INTO properties VALUES ('P92', 'E63', 'E77','brought into existence');
INSERT INTO properties VALUES ('P93', 'E64', 'E77','took out of existence');
INSERT INTO properties VALUES ('P94', 'E65', 'E28','has created');
INSERT INTO properties VALUES ('-P94', 'E28', 'E65','was created by');
INSERT INTO properties VALUES ('P95', 'E66', 'E74','has formed');
INSERT INTO properties VALUES ('-P95', 'E74', 'E66','was formed by');
INSERT INTO properties VALUES ('P96', 'E67', 'E21','by mother');
INSERT INTO properties VALUES ('P97', 'E67', 'E21','from father');
INSERT INTO properties VALUES ('-P97', 'E21', 'E67','was father for');
INSERT INTO properties VALUES ('-P98', 'E21', 'E67','was born');
INSERT INTO properties VALUES ('P99', 'E68', 'E74','dissolved');
INSERT INTO properties VALUES ('-P99', 'E74', 'E68','was dissolved by');
INSERT INTO properties VALUES ('-P112', 'E24', 'E80','was diminished by');
INSERT INTO properties VALUES ('-P115', 'E2', 'E2','is finished by');
INSERT INTO properties VALUES ('P118', 'E2', 'E2','overlaps in time with');
INSERT INTO properties VALUES ('-P119', 'E2', 'E2','is met in time by');
INSERT INTO properties VALUES ('-P120', 'E2', 'E2','occurs  after');
INSERT INTO properties VALUES ('-P123', 'E77', 'E81','resulted from');
INSERT INTO properties VALUES ('P125', 'E7', 'E55','used object of type');
INSERT INTO properties VALUES ('-P126', 'E57', 'E11','was employed in');
INSERT INTO properties VALUES ('-P128', 'E73', 'E24','is carried by');
INSERT INTO properties VALUES ('P130', 'E70', 'E70','shows features of');
INSERT INTO properties VALUES ('-P131', 'E82', 'E39','identifies');
INSERT INTO properties VALUES ('-P134', 'E7', 'E7','was continued by');
INSERT INTO properties VALUES ('-P136', 'E1', 'E83','supported type creation');
INSERT INTO properties VALUES ('-P138', 'E1', 'E36','has representation');
INSERT INTO properties VALUES ('P140', 'E13', 'E1','assigned attribute to');
INSERT INTO properties VALUES ('P142', 'E15', 'E41','used constituent');
INSERT INTO properties VALUES ('P144', 'E85', 'E74','joined with');
INSERT INTO properties VALUES ('-P146', 'E74', 'E86','lost member by');
INSERT INTO properties VALUES ('-P148', 'E89', 'E89','is component of');
INSERT INTO properties VALUES ('-P16', 'E70', 'E7','was used for');
INSERT INTO properties VALUES ('-P19', 'E71', 'E7','was made for');
INSERT INTO properties VALUES ('P21', 'E7', 'E55','had general purpose');
INSERT INTO properties VALUES ('-P22', 'E39', 'E8','acquired title through');
INSERT INTO properties VALUES ('P24', 'E8', 'E18','transferred title of');
INSERT INTO properties VALUES ('-P26', 'E53', 'E9','was destination of');
INSERT INTO properties VALUES ('-P28', 'E39', 'E10','surrendered custody through');
INSERT INTO properties VALUES ('P3', 'E1', 'E62','has note');
INSERT INTO properties VALUES ('-P30', 'E18', 'E10','custody transferred through');
INSERT INTO properties VALUES ('-P31', 'E24', 'E11','was modified by');
INSERT INTO properties VALUES ('-P33', 'E29', 'E11','was used by');
INSERT INTO properties VALUES ('-P35', 'E3', 'E14','identified by');
INSERT INTO properties VALUES ('P39', 'E16', 'E1','measured');
INSERT INTO properties VALUES ('P40', 'E16', 'E54','observed dimension');
INSERT INTO properties VALUES ('P42', 'E17', 'E55','assigned');
INSERT INTO properties VALUES ('-P44', 'E3', 'E18','is condition of');
INSERT INTO properties VALUES ('P46', 'E18', 'E18','is composed of');
INSERT INTO properties VALUES ('-P48', 'E42', 'E1','is preferred identifier of');
INSERT INTO properties VALUES ('P5', 'E3', 'E3','consists of');
INSERT INTO properties VALUES ('-P50', 'E39', 'E18','is current keeper of');
INSERT INTO properties VALUES ('P52', 'E18', 'E39','has current owner');
INSERT INTO properties VALUES ('P53', 'E18', 'E53','has former or current location');
INSERT INTO properties VALUES ('-P54', 'E53', 'E19','is current permanent location of');
INSERT INTO properties VALUES ('-P56', 'E26', 'E19','is found on');
INSERT INTO properties VALUES ('-P58', 'E46', 'E18','defines section');
INSERT INTO properties VALUES ('P65', 'E24', 'E36','shows visual item');
INSERT INTO properties VALUES ('P68', 'E29', 'E57','foresees use of');
INSERT INTO properties VALUES ('-P7', 'E53', 'E4','witnessed');
INSERT INTO properties VALUES ('P72', 'E33', 'E56','has language');
INSERT INTO properties VALUES ('-P73', 'E33', 'E33','is translation of');
INSERT INTO properties VALUES ('P75', 'E39', 'E30','possesses');
INSERT INTO properties VALUES ('-P76', 'E51', 'E39','provides access to');
INSERT INTO properties VALUES ('P8', 'E4', 'E19','took place on or within');
INSERT INTO properties VALUES ('P82', 'E52', 'E61','at some time within');
INSERT INTO properties VALUES ('P84', 'E52', 'E54','had at most duration');
INSERT INTO properties VALUES ('-P86', 'E52', 'E52','contains');
INSERT INTO properties VALUES ('-P88', 'E53', 'E53','forms part of');
INSERT INTO properties VALUES ('-P9', 'E4', 'E4','forms part of');
INSERT INTO properties VALUES ('-P92', 'E77', 'E63','was brought into existence by');
INSERT INTO properties VALUES ('-P93', 'E77', 'E64','was taken out of existence by');
INSERT INTO properties VALUES ('-P96', 'E21', 'E67','gave birth');
INSERT INTO properties VALUES ('P98', 'E67', 'E21','brought into life');
INSERT INTO properties VALUES ('BM.PX.is_related_to', 'E18', 'E18','is related to');
INSERT INTO properties VALUES ('P14.1', 'E7', 'E39','in the role of');


-- Completed on 2013-06-25 15:32:29

--
-- PostgreSQL database dump complete
--

SET search_path = data, pg_catalog;

INSERT INTO entity_types(classid, conceptid, businesstablename, publishbydefault, entitytypeid, isresource)
    VALUES ('E55', '00000000-0000-0000-0000-000000000005', 'domains', false, 'ARCHES_RESOURCE_CROSS-REFERENCE_RELATIONSHIP_TYPES.E55', false);

INSERT INTO concepts.relations VALUES ('00000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000005', 'hasCollection', public.uuid_generate_v1mc());
