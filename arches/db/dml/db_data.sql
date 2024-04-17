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

INSERT INTO d_languages VALUES ('en', 'ENGLISH', true);


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
INSERT INTO d_value_types VALUES ('min_year', 'undefined', null, 'arches', 'text');
INSERT INTO d_value_types VALUES ('max_year', 'undefined', null, 'arches', 'text');

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

--OWL Class types and Arches specific types
INSERT INTO d_node_types VALUES ('ConceptScheme', 'skos');
INSERT INTO d_node_types VALUES ('Concept', 'skos');
INSERT INTO d_node_types VALUES ('Collection', 'skos');


INSERT INTO concepts(conceptid, nodetype, legacyoid) VALUES ('00000000-0000-0000-0000-000000000001', 'ConceptScheme', 'ARCHES');
INSERT INTO concepts(conceptid, nodetype, legacyoid) VALUES ('00000000-0000-0000-0000-000000000004', 'Concept', 'ARCHES RESOURCE CROSS-REFERENCE RELATIONSHIP TYPES CONCEPT');
INSERT INTO concepts(conceptid, nodetype, legacyoid) VALUES ('00000000-0000-0000-0000-000000000005', 'Collection', 'ARCHES RESOURCE CROSS-REFERENCE RELATIONSHIP TYPES COLLECTION');
INSERT INTO concepts(conceptid, nodetype, legacyoid) VALUES ('00000000-0000-0000-0000-000000000006', 'ConceptScheme', 'CANDIDATES');
INSERT INTO concepts(conceptid, nodetype, legacyoid) VALUES ('00000000-0000-0000-0000-000000000007', 'Concept', 'DEFAULT RESOURCE TO RESOURCE RELATIONSHIP TYPE');


INSERT INTO values(valueid, conceptid, valuetype, value, languageid) VALUES ('d8c60bf4-e786-11e6-905a-b756ec83dad5', '00000000-0000-0000-0000-000000000001', 'prefLabel', 'Arches', 'en');
INSERT INTO values(valueid, conceptid, valuetype, value, languageid) VALUES ('c12e7e6c-e417-11e6-b14b-0738913905b4', '00000000-0000-0000-0000-000000000004', 'prefLabel', 'Resource To Resource Relationship Types', 'en');
INSERT INTO values(valueid, conceptid, valuetype, value, languageid) VALUES ('d8c622f6-e786-11e6-905a-475a5eee86f5', '00000000-0000-0000-0000-000000000005', 'prefLabel', 'Resource To Resource Relationship Types', 'en');
INSERT INTO values(valueid, conceptid, valuetype, value, languageid) VALUES ('fee39428-e83f-11e6-b49d-9b976819ac02', '00000000-0000-0000-0000-000000000006', 'prefLabel', 'Candidates', 'en');
INSERT INTO values(valueid, conceptid, valuetype, value, languageid) VALUES ('ac41d9be-79db-4256-b368-2f4559cfbe55', '00000000-0000-0000-0000-000000000007', 'prefLabel', 'is related to', 'en');


INSERT INTO relations(relationid, conceptidfrom, conceptidto, relationtype)
    VALUES (public.uuid_generate_v1mc(), '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000004', 'hasTopConcept');

INSERT INTO relations(relationid, conceptidfrom, conceptidto, relationtype)
    VALUES (public.uuid_generate_v1mc(), '00000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000007', 'member');


SET search_path = public, pg_catalog;

INSERT INTO auth_user(username, first_name, last_name, email, password, is_staff, is_active, is_superuser, last_login, date_joined)
    VALUES ('admin', '', '', '', 'pbkdf2_sha256$24000$NjdJsyUb6vMd$YM3B8ImPgpF4Mr+jBSFnKu+P5jNmxD/mqwxQUXaLLmI=', 't', 't', 't', '2012-03-15 15:29:31.211-07', '2012-03-15 15:29:31.211-07');

INSERT INTO auth_user(username, first_name, last_name, email, password, is_staff, is_active, is_superuser, last_login, date_joined)
    VALUES ('anonymous', '', '', '', '!S9npj7MhUqm30gT5ldm4TposL8jU5jDL4Ab02uuK', 'f', 't', 'f', '2012-03-15 15:29:31.211-07', '2012-03-15 15:29:31.211-07');

INSERT INTO widgets(widgetid, name, component, datatype, defaultconfig)
    VALUES ('10000000-0000-0000-0000-000000000001', 'text-widget', 'views/components/widgets/text', 'string', '{ "placeholder": "Enter text", "width": "100%", "maxLength": null}');

INSERT INTO widgets(widgetid, name, component, datatype, defaultconfig)
    VALUES ('10000000-0000-0000-0000-000000000002', 'concept-select-widget', 'views/components/widgets/concept-select', 'concept', '{ "placeholder": "Select an option", "options": [] }');

INSERT INTO widgets(widgetid, name, component, datatype, defaultconfig)
    VALUES ('10000000-0000-0000-0000-000000000012', 'concept-multiselect-widget', 'views/components/widgets/concept-multiselect', 'concept-list', '{ "placeholder": "Select an option", "options": [] }');

INSERT INTO widgets(widgetid, name, component, datatype, defaultconfig)
    VALUES ('10000000-0000-0000-0000-000000000015', 'domain-select-widget', 'views/components/widgets/domain-select', 'domain-value', '{ "placeholder": "Select an option" }');

INSERT INTO widgets(widgetid, name, component, datatype, defaultconfig)
    VALUES ('10000000-0000-0000-0000-000000000016', 'domain-multiselect-widget', 'views/components/widgets/domain-multiselect', 'domain-value-list', '{ "placeholder": "Select an option" }');

INSERT INTO widgets(widgetid, name, component, datatype, defaultconfig)
    VALUES ('10000000-0000-0000-0000-000000000003', 'switch-widget', 'views/components/widgets/switch', 'boolean', '{ "subtitle": "Click to switch"}');

INSERT INTO widgets(widgetid, name, component, datatype, defaultconfig)
    VALUES ('10000000-0000-0000-0000-000000000004', 'datepicker-widget', 'views/components/widgets/datepicker', 'date',
    '{
        "placeholder": "Enter date",
        "viewMode": "days",
        "dateFormat": "YYYY-MM-DD",
        "minDate": false,
        "maxDate": false
    }'
);

INSERT INTO widgets(widgetid, name, component, datatype, defaultconfig)
    VALUES ('10000000-0000-0000-0000-000000000005', 'rich-text-widget', 'views/components/widgets/rich-text', 'string', '{}');

INSERT INTO widgets(widgetid, name, component, datatype, defaultconfig)
    VALUES ('10000000-0000-0000-0000-000000000006', 'radio-boolean-widget', 'views/components/widgets/radio-boolean', 'boolean', '{"trueLabel": "Yes", "falseLabel": "No"}');

INSERT INTO widgets(widgetid, name, component, datatype, defaultconfig)
    VALUES ('10000000-0000-0000-0000-000000000007', 'map-widget', 'views/components/widgets/map', 'geojson-feature-collection',
    '{
        "basemap": "streets",
        "geometryTypes": [{"text":"Point", "id":"Point"}, {"text":"Line", "id":"Line"}, {"text":"Polygon", "id":"Polygon"}],
        "overlayConfigs": [],
        "overlayOpacity": 0.0,
        "geocodeProvider": "MapzenGeocoder",
        "zoom": 0,
        "maxZoom": 20,
        "minZoom": 0,
        "centerX": 0,
        "centerY": 0,
        "pitch": 0.0,
        "bearing": 0.0,
        "geocodePlaceholder": "Search",
        "geocoderVisible": true,
        "featureColor": null,
        "featureLineWidth": null,
        "featurePointSize": null
    }'
);

INSERT INTO widgets(widgetid, name, component, datatype, defaultconfig)
    VALUES ('10000000-0000-0000-0000-000000000008', 'number-widget', 'views/components/widgets/number', 'number', '{ "placeholder": "Enter number", "width": "100%", "min":"", "max":""}');

INSERT INTO widgets(widgetid, name, component, datatype, defaultconfig)
    VALUES ('10000000-0000-0000-0000-000000000009', 'concept-radio-widget', 'views/components/widgets/concept-radio', 'concept', '{ "options": [] }');

INSERT INTO widgets(widgetid, name, component, datatype, defaultconfig)
    VALUES ('10000000-0000-0000-0000-000000000013', 'concept-checkbox-widget', 'views/components/widgets/concept-checkbox', 'concept-list', '{ "options": [] }');

INSERT INTO widgets(widgetid, name, component, datatype, defaultconfig)
    VALUES ('10000000-0000-0000-0000-000000000017', 'domain-radio-widget', 'views/components/widgets/domain-radio', 'domain-value', '{}');

INSERT INTO widgets(widgetid, name, component, datatype, defaultconfig)
    VALUES ('10000000-0000-0000-0000-000000000018', 'domain-checkbox-widget', 'views/components/widgets/domain-checkbox', 'domain-value-list', '{}');

INSERT INTO widgets(widgetid, name, component, datatype, defaultconfig)
    VALUES ('10000000-0000-0000-0000-000000000019', 'file-widget', 'views/components/widgets/file', 'file-list', '{"acceptedFiles": "", "maxFilesize": "200"}');

--Data types
INSERT INTO d_data_types(datatype, iconclass, modulename, classname, defaultconfig, configcomponent, configname, isgeometric, defaultwidget) VALUES ('string', 'fa fa-file-code-o', 'datatypes.py', 'StringDataType',  null, null, null, FALSE, '10000000-0000-0000-0000-000000000001');
INSERT INTO d_data_types(datatype, iconclass, modulename, classname, defaultconfig, configcomponent, configname, isgeometric, defaultwidget) VALUES ('number', 'fa fa-hashtag', 'datatypes.py', 'NumberDataType', null, null, null, FALSE, '10000000-0000-0000-0000-000000000008');
INSERT INTO d_data_types(datatype, iconclass, modulename, classname, defaultconfig, configcomponent, configname, isgeometric, defaultwidget) VALUES ('date', 'fa fa-calendar', 'datatypes.py', 'DateDataType', null, null, null, FALSE, '10000000-0000-0000-0000-000000000004');
INSERT INTO d_data_types(datatype, iconclass, modulename, classname, defaultconfig, configcomponent, configname, isgeometric, defaultwidget) VALUES ('geojson-feature-collection', 'fa fa-globe', 'datatypes.py', 'GeojsonFeatureCollectionDataType', '{
    "pointColor": "rgba(130, 130, 130, 0.7)",
    "pointHaloColor": "rgba(200, 200, 200, 0.5)",
    "radius": 2,
    "haloRadius": 4,
    "lineColor": "rgba(130, 130, 130, 0.7)",
    "lineHaloColor": "rgba(200, 200, 200, 0.5)",
    "weight": 2,
    "haloWeight": 4,
    "fillColor": "rgba(130, 130, 130, 0.5)",
    "outlineColor": "rgba(200, 200, 200, 0.7)",
    "outlineWeight": 2,
    "layerActivated": true,
    "addToMap": false, "layerIcon": "",
    "layerName": "",
    "clusterDistance": 20,
    "clusterMaxZoom": 5,
    "clusterMinPoints": 3,
    "cacheTiles": false,
    "autoManageCache": false,
    "advancedStyling": false,
    "advancedStyle": ""
}', 'views/graph/datatypes/geojson-feature-collection', 'geojson-feature-collection-datatype-config', TRUE, '10000000-0000-0000-0000-000000000007');
INSERT INTO d_data_types(datatype, iconclass, modulename, classname, defaultconfig, configcomponent, configname, isgeometric, defaultwidget) VALUES ('concept', 'fa fa-list-ul', 'concept_types.py', 'ConceptDataType', '{"rdmCollection": null}', 'views/graph/datatypes/concept', 'concept-datatype-config', FALSE, '10000000-0000-0000-0000-000000000002');
INSERT INTO d_data_types(datatype, iconclass, modulename, classname, defaultconfig, configcomponent, configname, isgeometric, defaultwidget) VALUES ('concept-list', 'fa fa-list-ul', 'concept_types.py', 'ConceptListDataType', '{"rdmCollection": null}', 'views/graph/datatypes/concept', 'concept-datatype-config', FALSE, '10000000-0000-0000-0000-000000000012');
INSERT INTO d_data_types(datatype, iconclass, modulename, classname, defaultconfig, configcomponent, configname, isgeometric, defaultwidget) VALUES ('domain-value', 'fa fa-list-ul', 'concept_types.py', 'ConceptDataType', '{"options": []}', 'views/graph/datatypes/domain-value', 'domain-value-datatype-config', FALSE, '10000000-0000-0000-0000-000000000015');
INSERT INTO d_data_types(datatype, iconclass, modulename, classname, defaultconfig, configcomponent, configname, isgeometric, defaultwidget) VALUES ('domain-value-list', 'fa fa-list-ul', 'concept_types.py', 'ConceptListDataType', '{"options": []}', 'views/graph/datatypes/domain-value', 'domain-value-datatype-config', FALSE, '10000000-0000-0000-0000-000000000016');
INSERT INTO d_data_types(datatype, iconclass, modulename, classname, defaultconfig, configcomponent, configname, isgeometric, defaultwidget) VALUES ('boolean', 'fa fa-toggle-on', 'datatypes.py', 'BooleanDataType', null, null, null, FALSE, '10000000-0000-0000-0000-000000000006');
INSERT INTO d_data_types(datatype, iconclass, modulename, classname, defaultconfig, configcomponent, configname, isgeometric, defaultwidget) VALUES ('file-list', 'fa fa-file-image-o', 'datatypes.py', 'FileListDataType', null, null, null, FALSE, '10000000-0000-0000-0000-000000000019');
INSERT INTO d_data_types(datatype, iconclass, modulename, classname, defaultconfig, configcomponent, configname, isgeometric) VALUES ('semantic', 'fa fa-link', 'datatypes.py', 'BaseDataType', null, null, null, FALSE);

-- Node graph
INSERT INTO graphs(graphid, name, author, version, description, isresource, isactive, iconclass, subtitle, ontologyid)
    VALUES ('22000000-0000-0000-0000-000000000000', 'Node', 'Arches', 'v1', 'Represents a single node in a graph', 'f', 't', 'fa fa-circle', 'Represents a single node in a graph.', null);

INSERT INTO nodes(nodeid, name, description, istopnode, ontologyclass, datatype, graphid)
    VALUES ('20000000-0000-0000-0000-100000000000', 'Node', 'Represents a single node in a graph', 't', 'E1_CRM_Entity', 'semantic', '22000000-0000-0000-0000-000000000000');

INSERT INTO node_groups(nodegroupid, legacygroupid, cardinality)
    VALUES ('20000000-0000-0000-0000-100000000000', '', 'n');
-- End Node graph

-- Node/NodeType graph
INSERT INTO graphs(graphid, name, author, version, description, isresource, isactive, iconclass, subtitle, ontologyid)
    VALUES ('22000000-0000-0000-0000-000000000001', 'Node/Node Type', 'Arches', 'v1', 'Represents a node and node type pairing', 'f',  't', 'fa fa-angle-double-down','Represents a node and node type pairing', null);

INSERT INTO node_groups(nodegroupid, legacygroupid, cardinality)
    VALUES ('20000000-0000-0000-0000-100000000001', '', 'n');

INSERT INTO nodes(nodeid, name, description, istopnode, ontologyclass, datatype,
            graphid, nodegroupid)
    VALUES ('20000000-0000-0000-0000-100000000001', 'Node', '', 't', 'E1_CRM_Entity', 'string',
            '22000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-100000000001');

INSERT INTO nodes(nodeid, name, description, istopnode, ontologyclass, datatype,
            graphid, nodegroupid, config)
    VALUES ('20000000-0000-0000-0000-100000000002', 'Node Type', '', 'f', 'E55_Type', 'concept',
            '22000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-100000000001', '{"rdmCollection": null}');


INSERT INTO edges(edgeid, graphid, domainnodeid, rangenodeid, ontologyproperty)
    VALUES ('22200000-0000-0000-0000-000000000001', '22000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-100000000001', '20000000-0000-0000-0000-100000000002', 'P2_has_type');

INSERT INTO cards(cardid, name, description, instructions,
        nodegroupid, graphid, active, visible, helpenabled)
    VALUES (public.uuid_generate_v1mc(), 'Node/Node Type', 'Represents a node and node type pairing', '',
        '20000000-0000-0000-0000-100000000001', '22000000-0000-0000-0000-000000000001', 't', 't', 'f');
-- End Node/NodeType graph



INSERT INTO icons(name, cssclass)
    VALUES ('cc', 'fa fa-cc');

INSERT INTO icons(name, cssclass)
    VALUES ('bookmark', 'fa fa-bookmark');

INSERT INTO icons(name, cssclass)
    VALUES ('venus-mars', 'fa fa-venus-mars');

INSERT INTO icons(name, cssclass)
    VALUES ('arrow-circle-o-down', 'fa fa-arrow-circle-o-down');

INSERT INTO icons(name, cssclass)
    VALUES ('comment-o', 'fa fa-comment-o');

INSERT INTO icons(name, cssclass)
    VALUES ('long-arrow-left', 'fa fa-long-arrow-left');

INSERT INTO icons(name, cssclass)
    VALUES ('arrow-right', 'fa fa-arrow-right');

INSERT INTO icons(name, cssclass)
    VALUES ('delicious', 'fa fa-delicious');

INSERT INTO icons(name, cssclass)
    VALUES ('chevron-circle-left', 'fa fa-chevron-circle-left');

INSERT INTO icons(name, cssclass)
    VALUES ('bullhorn', 'fa fa-bullhorn');

INSERT INTO icons(name, cssclass)
    VALUES ('outdent', 'fa fa-outdent');

INSERT INTO icons(name, cssclass)
    VALUES ('jpy', 'fa fa-jpy');

INSERT INTO icons(name, cssclass)
    VALUES ('drupal', 'fa fa-drupal');

INSERT INTO icons(name, cssclass)
    VALUES ('hdd-o', 'fa fa-hdd-o');

INSERT INTO icons(name, cssclass)
    VALUES ('hand-o-left', 'fa fa-hand-o-left');

INSERT INTO icons(name, cssclass)
    VALUES ('pinterest', 'fa fa-pinterest');

INSERT INTO icons(name, cssclass)
    VALUES ('plane', 'fa fa-plane');

INSERT INTO icons(name, cssclass)
    VALUES ('question', 'fa fa-question');

INSERT INTO icons(name, cssclass)
    VALUES ('child', 'fa fa-child');

INSERT INTO icons(name, cssclass)
    VALUES ('circle-o', 'fa fa-circle-o');

INSERT INTO icons(name, cssclass)
    VALUES ('italic', 'fa fa-italic');

INSERT INTO icons(name, cssclass)
    VALUES ('meanpath', 'fa fa-meanpath');

INSERT INTO icons(name, cssclass)
    VALUES ('subway', 'fa fa-subway');

INSERT INTO icons(name, cssclass)
    VALUES ('google-plus', 'fa fa-google-plus');

INSERT INTO icons(name, cssclass)
    VALUES ('angle-up', 'fa fa-angle-up');

INSERT INTO icons(name, cssclass)
    VALUES ('star', 'fa fa-star');

INSERT INTO icons(name, cssclass)
    VALUES ('star-half-empty', 'fa fa-star-half-empty');

INSERT INTO icons(name, cssclass)
    VALUES ('facebook-official', 'fa fa-facebook-official');

INSERT INTO icons(name, cssclass)
    VALUES ('youtube-square', 'fa fa-youtube-square');

INSERT INTO icons(name, cssclass)
    VALUES ('rss', 'fa fa-rss');

INSERT INTO icons(name, cssclass)
    VALUES ('toggle-off', 'fa fa-toggle-off');

INSERT INTO icons(name, cssclass)
    VALUES ('list-ol', 'fa fa-list-ol');

INSERT INTO icons(name, cssclass)
    VALUES ('dot-circle-o', 'fa fa-dot-circle-o');

INSERT INTO icons(name, cssclass)
    VALUES ('copyright', 'fa fa-copyright');

INSERT INTO icons(name, cssclass)
    VALUES ('user', 'fa fa-user');

INSERT INTO icons(name, cssclass)
    VALUES ('key', 'fa fa-key');

INSERT INTO icons(name, cssclass)
    VALUES ('minus-square-o', 'fa fa-minus-square-o');

INSERT INTO icons(name, cssclass)
    VALUES ('mobile', 'fa fa-mobile');

INSERT INTO icons(name, cssclass)
    VALUES ('table', 'fa fa-table');

INSERT INTO icons(name, cssclass)
    VALUES ('columns', 'fa fa-columns');

INSERT INTO icons(name, cssclass)
    VALUES ('bolt', 'fa fa-bolt');

INSERT INTO icons(name, cssclass)
    VALUES ('fighter-jet', 'fa fa-fighter-jet');

INSERT INTO icons(name, cssclass)
    VALUES ('share-square-o', 'fa fa-share-square-o');

INSERT INTO icons(name, cssclass)
    VALUES ('file-archive-o', 'fa fa-file-archive-o');

INSERT INTO icons(name, cssclass)
    VALUES ('retweet', 'fa fa-retweet');

INSERT INTO icons(name, cssclass)
    VALUES ('level-up', 'fa fa-level-up');

INSERT INTO icons(name, cssclass)
    VALUES ('caret-left', 'fa fa-caret-left');

INSERT INTO icons(name, cssclass)
    VALUES ('arrow-circle-o-left', 'fa fa-arrow-circle-o-left');

INSERT INTO icons(name, cssclass)
    VALUES ('wrench', 'fa fa-wrench');

INSERT INTO icons(name, cssclass)
    VALUES ('shekel', 'fa fa-shekel');

INSERT INTO icons(name, cssclass)
    VALUES ('eraser', 'fa fa-eraser');

INSERT INTO icons(name, cssclass)
    VALUES ('sort-amount-asc', 'fa fa-sort-amount-asc');

INSERT INTO icons(name, cssclass)
    VALUES ('vimeo-square', 'fa fa-vimeo-square');

INSERT INTO icons(name, cssclass)
    VALUES ('gittip', 'fa fa-gittip');

INSERT INTO icons(name, cssclass)
    VALUES ('cube', 'fa fa-cube');

INSERT INTO icons(name, cssclass)
    VALUES ('phone-square', 'fa fa-phone-square');

INSERT INTO icons(name, cssclass)
    VALUES ('sort-asc', 'fa fa-sort-asc');

INSERT INTO icons(name, cssclass)
    VALUES ('skyatlas', 'fa fa-skyatlas');

INSERT INTO icons(name, cssclass)
    VALUES ('beer', 'fa fa-beer');

INSERT INTO icons(name, cssclass)
    VALUES ('behance-square', 'fa fa-behance-square');

INSERT INTO icons(name, cssclass)
    VALUES ('binoculars', 'fa fa-binoculars');

INSERT INTO icons(name, cssclass)
    VALUES ('folder-open', 'fa fa-folder-open');

INSERT INTO icons(name, cssclass)
    VALUES ('paint-brush', 'fa fa-paint-brush');

INSERT INTO icons(name, cssclass)
    VALUES ('whatsapp', 'fa fa-whatsapp');

INSERT INTO icons(name, cssclass)
    VALUES ('picture-o', 'fa fa-picture-o');

INSERT INTO icons(name, cssclass)
    VALUES ('sort-down', 'fa fa-sort-down');

INSERT INTO icons(name, cssclass)
    VALUES ('chevron-circle-up', 'fa fa-chevron-circle-up');

INSERT INTO icons(name, cssclass)
    VALUES ('bell-slash-o', 'fa fa-bell-slash-o');

INSERT INTO icons(name, cssclass)
    VALUES ('image', 'fa fa-image');

INSERT INTO icons(name, cssclass)
    VALUES ('tumblr-square', 'fa fa-tumblr-square');

INSERT INTO icons(name, cssclass)
    VALUES ('repeat', 'fa fa-repeat');

INSERT INTO icons(name, cssclass)
    VALUES ('wheelchair', 'fa fa-wheelchair');

INSERT INTO icons(name, cssclass)
    VALUES ('underline', 'fa fa-underline');

INSERT INTO icons(name, cssclass)
    VALUES ('group', 'fa fa-group');

INSERT INTO icons(name, cssclass)
    VALUES ('cab', 'fa fa-cab');

INSERT INTO icons(name, cssclass)
    VALUES ('thumbs-down', 'fa fa-thumbs-down');

INSERT INTO icons(name, cssclass)
    VALUES ('step-backward', 'fa fa-step-backward');

INSERT INTO icons(name, cssclass)
    VALUES ('expand', 'fa fa-expand');

INSERT INTO icons(name, cssclass)
    VALUES ('th-list', 'fa fa-th-list');

INSERT INTO icons(name, cssclass)
    VALUES ('renren', 'fa fa-renren');

INSERT INTO icons(name, cssclass)
    VALUES ('list-ul', 'fa fa-list-ul');

INSERT INTO icons(name, cssclass)
    VALUES ('flash', 'fa fa-flash');

INSERT INTO icons(name, cssclass)
    VALUES ('certificate', 'fa fa-certificate');

INSERT INTO icons(name, cssclass)
    VALUES ('thumbs-up', 'fa fa-thumbs-up');

INSERT INTO icons(name, cssclass)
    VALUES ('cc-amex', 'fa fa-cc-amex');

INSERT INTO icons(name, cssclass)
    VALUES ('empire', 'fa fa-empire');

INSERT INTO icons(name, cssclass)
    VALUES ('random', 'fa fa-random');

INSERT INTO icons(name, cssclass)
    VALUES ('database', 'fa fa-database');

INSERT INTO icons(name, cssclass)
    VALUES ('check-square', 'fa fa-check-square');

INSERT INTO icons(name, cssclass)
    VALUES ('search-minus', 'fa fa-search-minus');

INSERT INTO icons(name, cssclass)
    VALUES ('volume-off', 'fa fa-volume-off');

INSERT INTO icons(name, cssclass)
    VALUES ('legal', 'fa fa-legal');

INSERT INTO icons(name, cssclass)
    VALUES ('slack', 'fa fa-slack');

INSERT INTO icons(name, cssclass)
    VALUES ('gavel', 'fa fa-gavel');

INSERT INTO icons(name, cssclass)
    VALUES ('quote-right', 'fa fa-quote-right');

INSERT INTO icons(name, cssclass)
    VALUES ('rebel', 'fa fa-rebel');

INSERT INTO icons(name, cssclass)
    VALUES ('external-link-square', 'fa fa-external-link-square');

INSERT INTO icons(name, cssclass)
    VALUES ('comments', 'fa fa-comments');

INSERT INTO icons(name, cssclass)
    VALUES ('dashcube', 'fa fa-dashcube');

INSERT INTO icons(name, cssclass)
    VALUES ('btc', 'fa fa-btc');

INSERT INTO icons(name, cssclass)
    VALUES ('terminal', 'fa fa-terminal');

INSERT INTO icons(name, cssclass)
    VALUES ('align-justify', 'fa fa-align-justify');

INSERT INTO icons(name, cssclass)
    VALUES ('font', 'fa fa-font');

INSERT INTO icons(name, cssclass)
    VALUES ('unlink', 'fa fa-unlink');

INSERT INTO icons(name, cssclass)
    VALUES ('arrow-circle-o-right', 'fa fa-arrow-circle-o-right');

INSERT INTO icons(name, cssclass)
    VALUES ('file-photo-o', 'fa fa-file-photo-o');

INSERT INTO icons(name, cssclass)
    VALUES ('hotel', 'fa fa-hotel');

INSERT INTO icons(name, cssclass)
    VALUES ('angle-double-left', 'fa fa-angle-double-left');

INSERT INTO icons(name, cssclass)
    VALUES ('map-marker', 'fa fa-map-marker');

INSERT INTO icons(name, cssclass)
    VALUES ('lightbulb-o', 'fa fa-lightbulb-o');

INSERT INTO icons(name, cssclass)
    VALUES ('buysellads', 'fa fa-buysellads');

INSERT INTO icons(name, cssclass)
    VALUES ('sort', 'fa fa-sort');

INSERT INTO icons(name, cssclass)
    VALUES ('file-sound-o', 'fa fa-file-sound-o');

INSERT INTO icons(name, cssclass)
    VALUES ('github', 'fa fa-github');

INSERT INTO icons(name, cssclass)
    VALUES ('comments-o', 'fa fa-comments-o');

INSERT INTO icons(name, cssclass)
    VALUES ('css3', 'fa fa-css3');

INSERT INTO icons(name, cssclass)
    VALUES ('instagram', 'fa fa-instagram');

INSERT INTO icons(name, cssclass)
    VALUES ('exclamation-circle', 'fa fa-exclamation-circle');

INSERT INTO icons(name, cssclass)
    VALUES ('street-view', 'fa fa-street-view');

INSERT INTO icons(name, cssclass)
    VALUES ('book', 'fa fa-book');

INSERT INTO icons(name, cssclass)
    VALUES ('unlock-alt', 'fa fa-unlock-alt');

INSERT INTO icons(name, cssclass)
    VALUES ('unlock', 'fa fa-unlock');

INSERT INTO icons(name, cssclass)
    VALUES ('facebook-f', 'fa fa-facebook-f');

INSERT INTO icons(name, cssclass)
    VALUES ('caret-square-o-left', 'fa fa-caret-square-o-left');

INSERT INTO icons(name, cssclass)
    VALUES ('flask', 'fa fa-flask');

INSERT INTO icons(name, cssclass)
    VALUES ('save', 'fa fa-save');

INSERT INTO icons(name, cssclass)
    VALUES ('file-excel-o', 'fa fa-file-excel-o');

INSERT INTO icons(name, cssclass)
    VALUES ('git', 'fa fa-git');

INSERT INTO icons(name, cssclass)
    VALUES ('headphones', 'fa fa-headphones');

INSERT INTO icons(name, cssclass)
    VALUES ('apple', 'fa fa-apple');

INSERT INTO icons(name, cssclass)
    VALUES ('th-large', 'fa fa-th-large');

INSERT INTO icons(name, cssclass)
    VALUES ('adjust', 'fa fa-adjust');

INSERT INTO icons(name, cssclass)
    VALUES ('minus-circle', 'fa fa-minus-circle');

INSERT INTO icons(name, cssclass)
    VALUES ('undo', 'fa fa-undo');

INSERT INTO icons(name, cssclass)
    VALUES ('angle-double-up', 'fa fa-angle-double-up');

INSERT INTO icons(name, cssclass)
    VALUES ('forward', 'fa fa-forward');

INSERT INTO icons(name, cssclass)
    VALUES ('file-picture-o', 'fa fa-file-picture-o');

INSERT INTO icons(name, cssclass)
    VALUES ('xing', 'fa fa-xing');

INSERT INTO icons(name, cssclass)
    VALUES ('wifi', 'fa fa-wifi');

INSERT INTO icons(name, cssclass)
    VALUES ('file-o', 'fa fa-file-o');

INSERT INTO icons(name, cssclass)
    VALUES ('ra', 'fa fa-ra');

INSERT INTO icons(name, cssclass)
    VALUES ('university', 'fa fa-university');

INSERT INTO icons(name, cssclass)
    VALUES ('truck', 'fa fa-truck');

INSERT INTO icons(name, cssclass)
    VALUES ('cloud-upload', 'fa fa-cloud-upload');

INSERT INTO icons(name, cssclass)
    VALUES ('graduation-cap', 'fa fa-graduation-cap');

INSERT INTO icons(name, cssclass)
    VALUES ('rotate-right', 'fa fa-rotate-right');

INSERT INTO icons(name, cssclass)
    VALUES ('bank', 'fa fa-bank');

INSERT INTO icons(name, cssclass)
    VALUES ('hand-o-up', 'fa fa-hand-o-up');

INSERT INTO icons(name, cssclass)
    VALUES ('soccer-ball-o', 'fa fa-soccer-ball-o');

INSERT INTO icons(name, cssclass)
    VALUES ('paypal', 'fa fa-paypal');

INSERT INTO icons(name, cssclass)
    VALUES ('behance', 'fa fa-behance');

INSERT INTO icons(name, cssclass)
    VALUES ('bar-chart', 'fa fa-bar-chart');

INSERT INTO icons(name, cssclass)
    VALUES ('institution', 'fa fa-institution');

INSERT INTO icons(name, cssclass)
    VALUES ('align-right', 'fa fa-align-right');

INSERT INTO icons(name, cssclass)
    VALUES ('stack-exchange', 'fa fa-stack-exchange');

INSERT INTO icons(name, cssclass)
    VALUES ('windows', 'fa fa-windows');

INSERT INTO icons(name, cssclass)
    VALUES ('space-shuttle', 'fa fa-space-shuttle');

INSERT INTO icons(name, cssclass)
    VALUES ('youtube-play', 'fa fa-youtube-play');

INSERT INTO icons(name, cssclass)
    VALUES ('phone', 'fa fa-phone');

INSERT INTO icons(name, cssclass)
    VALUES ('ruble', 'fa fa-ruble');

INSERT INTO icons(name, cssclass)
    VALUES ('share-alt', 'fa fa-share-alt');

INSERT INTO icons(name, cssclass)
    VALUES ('inbox', 'fa fa-inbox');

INSERT INTO icons(name, cssclass)
    VALUES ('fire', 'fa fa-fire');

INSERT INTO icons(name, cssclass)
    VALUES ('steam-square', 'fa fa-steam-square');

INSERT INTO icons(name, cssclass)
    VALUES ('calendar-o', 'fa fa-calendar-o');

INSERT INTO icons(name, cssclass)
    VALUES ('comment', 'fa fa-comment');

INSERT INTO icons(name, cssclass)
    VALUES ('quote-left', 'fa fa-quote-left');

INSERT INTO icons(name, cssclass)
    VALUES ('tencent-weibo', 'fa fa-tencent-weibo');

INSERT INTO icons(name, cssclass)
    VALUES ('git-square', 'fa fa-git-square');

INSERT INTO icons(name, cssclass)
    VALUES ('sign-out', 'fa fa-sign-out');

INSERT INTO icons(name, cssclass)
    VALUES ('neuter', 'fa fa-neuter');

INSERT INTO icons(name, cssclass)
    VALUES ('newspaper-o', 'fa fa-newspaper-o');

INSERT INTO icons(name, cssclass)
    VALUES ('leanpub', 'fa fa-leanpub');

INSERT INTO icons(name, cssclass)
    VALUES ('angellist', 'fa fa-angellist');

INSERT INTO icons(name, cssclass)
    VALUES ('stop', 'fa fa-stop');

INSERT INTO icons(name, cssclass)
    VALUES ('gratipay', 'fa fa-gratipay');

INSERT INTO icons(name, cssclass)
    VALUES ('sort-numeric-desc', 'fa fa-sort-numeric-desc');

INSERT INTO icons(name, cssclass)
    VALUES ('heart-o', 'fa fa-heart-o');

INSERT INTO icons(name, cssclass)
    VALUES ('calculator', 'fa fa-calculator');

INSERT INTO icons(name, cssclass)
    VALUES ('mars-stroke-v', 'fa fa-mars-stroke-v');

INSERT INTO icons(name, cssclass)
    VALUES ('turkish-lira', 'fa fa-turkish-lira');

INSERT INTO icons(name, cssclass)
    VALUES ('search', 'fa fa-search');

INSERT INTO icons(name, cssclass)
    VALUES ('calendar', 'fa fa-calendar');

INSERT INTO icons(name, cssclass)
    VALUES ('cc-stripe', 'fa fa-cc-stripe');

INSERT INTO icons(name, cssclass)
    VALUES ('star-half-full', 'fa fa-star-half-full');

INSERT INTO icons(name, cssclass)
    VALUES ('fast-backward', 'fa fa-fast-backward');

INSERT INTO icons(name, cssclass)
    VALUES ('stumbleupon-circle', 'fa fa-stumbleupon-circle');

INSERT INTO icons(name, cssclass)
    VALUES ('check-circle', 'fa fa-check-circle');

INSERT INTO icons(name, cssclass)
    VALUES ('rub', 'fa fa-rub');

INSERT INTO icons(name, cssclass)
    VALUES ('edit', 'fa fa-edit');

INSERT INTO icons(name, cssclass)
    VALUES ('microphone', 'fa fa-microphone');

INSERT INTO icons(name, cssclass)
    VALUES ('html5', 'fa fa-html5');

INSERT INTO icons(name, cssclass)
    VALUES ('remove', 'fa fa-remove');

INSERT INTO icons(name, cssclass)
    VALUES ('signal', 'fa fa-signal');

INSERT INTO icons(name, cssclass)
    VALUES ('plus-square', 'fa fa-plus-square');

INSERT INTO icons(name, cssclass)
    VALUES ('bold', 'fa fa-bold');

INSERT INTO icons(name, cssclass)
    VALUES ('wordpress', 'fa fa-wordpress');

INSERT INTO icons(name, cssclass)
    VALUES ('usd', 'fa fa-usd');

INSERT INTO icons(name, cssclass)
    VALUES ('facebook', 'fa fa-facebook');

INSERT INTO icons(name, cssclass)
    VALUES ('lock', 'fa fa-lock');

INSERT INTO icons(name, cssclass)
    VALUES ('caret-down', 'fa fa-caret-down');

INSERT INTO icons(name, cssclass)
    VALUES ('ioxhost', 'fa fa-ioxhost');

INSERT INTO icons(name, cssclass)
    VALUES ('bell-slash', 'fa fa-bell-slash');

INSERT INTO icons(name, cssclass)
    VALUES ('long-arrow-down', 'fa fa-long-arrow-down');

INSERT INTO icons(name, cssclass)
    VALUES ('recycle', 'fa fa-recycle');

INSERT INTO icons(name, cssclass)
    VALUES ('print', 'fa fa-print');

INSERT INTO icons(name, cssclass)
    VALUES ('stumbleupon', 'fa fa-stumbleupon');

INSERT INTO icons(name, cssclass)
    VALUES ('filter', 'fa fa-filter');

INSERT INTO icons(name, cssclass)
    VALUES ('vine', 'fa fa-vine');

INSERT INTO icons(name, cssclass)
    VALUES ('share-alt-square', 'fa fa-share-alt-square');

INSERT INTO icons(name, cssclass)
    VALUES ('arrow-circle-up', 'fa fa-arrow-circle-up');

INSERT INTO icons(name, cssclass)
    VALUES ('heartbeat', 'fa fa-heartbeat');

INSERT INTO icons(name, cssclass)
    VALUES ('rupee', 'fa fa-rupee');

INSERT INTO icons(name, cssclass)
    VALUES ('toggle-on', 'fa fa-toggle-on');

INSERT INTO icons(name, cssclass)
    VALUES ('toggle-right', 'fa fa-toggle-right');

INSERT INTO icons(name, cssclass)
    VALUES ('play-circle-o', 'fa fa-play-circle-o');

INSERT INTO icons(name, cssclass)
    VALUES ('microphone-slash', 'fa fa-microphone-slash');

INSERT INTO icons(name, cssclass)
    VALUES ('sort-numeric-asc', 'fa fa-sort-numeric-asc');

INSERT INTO icons(name, cssclass)
    VALUES ('cc-mastercard', 'fa fa-cc-mastercard');

INSERT INTO icons(name, cssclass)
    VALUES ('life-bouy', 'fa fa-life-bouy');

INSERT INTO icons(name, cssclass)
    VALUES ('chevron-left', 'fa fa-chevron-left');

INSERT INTO icons(name, cssclass)
    VALUES ('ellipsis-v', 'fa fa-ellipsis-v');

INSERT INTO icons(name, cssclass)
    VALUES ('folder-open-o', 'fa fa-folder-open-o');

INSERT INTO icons(name, cssclass)
    VALUES ('pencil', 'fa fa-pencil');

INSERT INTO icons(name, cssclass)
    VALUES ('file-video-o', 'fa fa-file-video-o');

INSERT INTO icons(name, cssclass)
    VALUES ('server', 'fa fa-server');

INSERT INTO icons(name, cssclass)
    VALUES ('train', 'fa fa-train');

INSERT INTO icons(name, cssclass)
    VALUES ('spotify', 'fa fa-spotify');

INSERT INTO icons(name, cssclass)
    VALUES ('simplybuilt', 'fa fa-simplybuilt');

INSERT INTO icons(name, cssclass)
    VALUES ('user-plus', 'fa fa-user-plus');

INSERT INTO icons(name, cssclass)
    VALUES ('file-movie-o', 'fa fa-file-movie-o');

INSERT INTO icons(name, cssclass)
    VALUES ('maxcdn', 'fa fa-maxcdn');

INSERT INTO icons(name, cssclass)
    VALUES ('krw', 'fa fa-krw');

INSERT INTO icons(name, cssclass)
    VALUES ('navicon', 'fa fa-navicon');

INSERT INTO icons(name, cssclass)
    VALUES ('angle-left', 'fa fa-angle-left');

INSERT INTO icons(name, cssclass)
    VALUES ('caret-square-o-right', 'fa fa-caret-square-o-right');

INSERT INTO icons(name, cssclass)
    VALUES ('mercury', 'fa fa-mercury');

INSERT INTO icons(name, cssclass)
    VALUES ('circle-thin', 'fa fa-circle-thin');

INSERT INTO icons(name, cssclass)
    VALUES ('text-width', 'fa fa-text-width');

INSERT INTO icons(name, cssclass)
    VALUES ('wechat', 'fa fa-wechat');

INSERT INTO icons(name, cssclass)
    VALUES ('reorder', 'fa fa-reorder');

INSERT INTO icons(name, cssclass)
    VALUES ('envelope-square', 'fa fa-envelope-square');

INSERT INTO icons(name, cssclass)
    VALUES ('bitbucket-square', 'fa fa-bitbucket-square');

INSERT INTO icons(name, cssclass)
    VALUES ('frown-o', 'fa fa-frown-o');

INSERT INTO icons(name, cssclass)
    VALUES ('line-chart', 'fa fa-line-chart');

INSERT INTO icons(name, cssclass)
    VALUES ('mars', 'fa fa-mars');

INSERT INTO icons(name, cssclass)
    VALUES ('arrow-circle-down', 'fa fa-arrow-circle-down');

INSERT INTO icons(name, cssclass)
    VALUES ('caret-up', 'fa fa-caret-up');

INSERT INTO icons(name, cssclass)
    VALUES ('tumblr', 'fa fa-tumblr');

INSERT INTO icons(name, cssclass)
    VALUES ('star-o', 'fa fa-star-o');

INSERT INTO icons(name, cssclass)
    VALUES ('cart-plus', 'fa fa-cart-plus');

INSERT INTO icons(name, cssclass)
    VALUES ('check', 'fa fa-check');

INSERT INTO icons(name, cssclass)
    VALUES ('lastfm', 'fa fa-lastfm');

INSERT INTO icons(name, cssclass)
    VALUES ('pencil-square', 'fa fa-pencil-square');

INSERT INTO icons(name, cssclass)
    VALUES ('trophy', 'fa fa-trophy');

INSERT INTO icons(name, cssclass)
    VALUES ('external-link', 'fa fa-external-link');

INSERT INTO icons(name, cssclass)
    VALUES ('long-arrow-up', 'fa fa-long-arrow-up');

INSERT INTO icons(name, cssclass)
    VALUES ('envelope-o', 'fa fa-envelope-o');

INSERT INTO icons(name, cssclass)
    VALUES ('user-times', 'fa fa-user-times');

INSERT INTO icons(name, cssclass)
    VALUES ('trello', 'fa fa-trello');

INSERT INTO icons(name, cssclass)
    VALUES ('file-powerpoint-o', 'fa fa-file-powerpoint-o');

INSERT INTO icons(name, cssclass)
    VALUES ('circle', 'fa fa-circle');

INSERT INTO icons(name, cssclass)
    VALUES ('paper-plane', 'fa fa-paper-plane');

INSERT INTO icons(name, cssclass)
    VALUES ('google', 'fa fa-google');

INSERT INTO icons(name, cssclass)
    VALUES ('bug', 'fa fa-bug');

INSERT INTO icons(name, cssclass)
    VALUES ('bitcoin', 'fa fa-bitcoin');

INSERT INTO icons(name, cssclass)
    VALUES ('lastfm-square', 'fa fa-lastfm-square');

INSERT INTO icons(name, cssclass)
    VALUES ('umbrella', 'fa fa-umbrella');

INSERT INTO icons(name, cssclass)
    VALUES ('text-height', 'fa fa-text-height');

INSERT INTO icons(name, cssclass)
    VALUES ('send-o', 'fa fa-send-o');

INSERT INTO icons(name, cssclass)
    VALUES ('support', 'fa fa-support');

INSERT INTO icons(name, cssclass)
    VALUES ('paw', 'fa fa-paw');

INSERT INTO icons(name, cssclass)
    VALUES ('cart-arrow-down', 'fa fa-cart-arrow-down');

INSERT INTO icons(name, cssclass)
    VALUES ('twitch', 'fa fa-twitch');

INSERT INTO icons(name, cssclass)
    VALUES ('crop', 'fa fa-crop');

INSERT INTO icons(name, cssclass)
    VALUES ('trash-o', 'fa fa-trash-o');

INSERT INTO icons(name, cssclass)
    VALUES ('file', 'fa fa-file');

INSERT INTO icons(name, cssclass)
    VALUES ('align-left', 'fa fa-align-left');

INSERT INTO icons(name, cssclass)
    VALUES ('user-md', 'fa fa-user-md');

INSERT INTO icons(name, cssclass)
    VALUES ('sellsy', 'fa fa-sellsy');

INSERT INTO icons(name, cssclass)
    VALUES ('github-alt', 'fa fa-github-alt');

INSERT INTO icons(name, cssclass)
    VALUES ('desktop', 'fa fa-desktop');

INSERT INTO icons(name, cssclass)
    VALUES ('info-circle', 'fa fa-info-circle');

INSERT INTO icons(name, cssclass)
    VALUES ('file-audio-o', 'fa fa-file-audio-o');

INSERT INTO icons(name, cssclass)
    VALUES ('compass', 'fa fa-compass');

INSERT INTO icons(name, cssclass)
    VALUES ('dribbble', 'fa fa-dribbble');

INSERT INTO icons(name, cssclass)
    VALUES ('fast-forward', 'fa fa-fast-forward');

INSERT INTO icons(name, cssclass)
    VALUES ('weixin', 'fa fa-weixin');

INSERT INTO icons(name, cssclass)
    VALUES ('adn', 'fa fa-adn');

INSERT INTO icons(name, cssclass)
    VALUES ('arrow-circle-o-up', 'fa fa-arrow-circle-o-up');

INSERT INTO icons(name, cssclass)
    VALUES ('eye', 'fa fa-eye');

INSERT INTO icons(name, cssclass)
    VALUES ('arrows-h', 'fa fa-arrows-h');

INSERT INTO icons(name, cssclass)
    VALUES ('archive', 'fa fa-archive');

INSERT INTO icons(name, cssclass)
    VALUES ('try', 'fa fa-try');

INSERT INTO icons(name, cssclass)
    VALUES ('reply', 'fa fa-reply');

INSERT INTO icons(name, cssclass)
    VALUES ('mail-reply-all', 'fa fa-mail-reply-all');

INSERT INTO icons(name, cssclass)
    VALUES ('backward', 'fa fa-backward');

INSERT INTO icons(name, cssclass)
    VALUES ('spinner', 'fa fa-spinner');

INSERT INTO icons(name, cssclass)
    VALUES ('arrow-left', 'fa fa-arrow-left');

INSERT INTO icons(name, cssclass)
    VALUES ('level-down', 'fa fa-level-down');

INSERT INTO icons(name, cssclass)
    VALUES ('suitcase', 'fa fa-suitcase');

INSERT INTO icons(name, cssclass)
    VALUES ('asterisk', 'fa fa-asterisk');

INSERT INTO icons(name, cssclass)
    VALUES ('file-word-o', 'fa fa-file-word-o');

INSERT INTO icons(name, cssclass)
    VALUES ('meh-o', 'fa fa-meh-o');

INSERT INTO icons(name, cssclass)
    VALUES ('moon-o', 'fa fa-moon-o');

INSERT INTO icons(name, cssclass)
    VALUES ('caret-right', 'fa fa-caret-right');

INSERT INTO icons(name, cssclass)
    VALUES ('smile-o', 'fa fa-smile-o');

INSERT INTO icons(name, cssclass)
    VALUES ('times-circle-o', 'fa fa-times-circle-o');

INSERT INTO icons(name, cssclass)
    VALUES ('play-circle', 'fa fa-play-circle');

INSERT INTO icons(name, cssclass)
    VALUES ('trash', 'fa fa-trash');

INSERT INTO icons(name, cssclass)
    VALUES ('deviantart', 'fa fa-deviantart');

INSERT INTO icons(name, cssclass)
    VALUES ('rocket', 'fa fa-rocket');

INSERT INTO icons(name, cssclass)
    VALUES ('play', 'fa fa-play');

INSERT INTO icons(name, cssclass)
    VALUES ('tasks', 'fa fa-tasks');

INSERT INTO icons(name, cssclass)
    VALUES ('cny', 'fa fa-cny');

INSERT INTO icons(name, cssclass)
    VALUES ('bars', 'fa fa-bars');

INSERT INTO icons(name, cssclass)
    VALUES ('tachometer', 'fa fa-tachometer');

INSERT INTO icons(name, cssclass)
    VALUES ('heart', 'fa fa-heart');

INSERT INTO icons(name, cssclass)
    VALUES ('star-half', 'fa fa-star-half');

INSERT INTO icons(name, cssclass)
    VALUES ('camera', 'fa fa-camera');

INSERT INTO icons(name, cssclass)
    VALUES ('music', 'fa fa-music');

INSERT INTO icons(name, cssclass)
    VALUES ('share-square', 'fa fa-share-square');

INSERT INTO icons(name, cssclass)
    VALUES ('birthday-cake', 'fa fa-birthday-cake');

INSERT INTO icons(name, cssclass)
    VALUES ('puzzle-piece', 'fa fa-puzzle-piece');

INSERT INTO icons(name, cssclass)
    VALUES ('arrow-circle-right', 'fa fa-arrow-circle-right');

INSERT INTO icons(name, cssclass)
    VALUES ('camera-retro', 'fa fa-camera-retro');

INSERT INTO icons(name, cssclass)
    VALUES ('sort-desc', 'fa fa-sort-desc');

INSERT INTO icons(name, cssclass)
    VALUES ('openid', 'fa fa-openid');

INSERT INTO icons(name, cssclass)
    VALUES ('language', 'fa fa-language');

INSERT INTO icons(name, cssclass)
    VALUES ('file-pdf-o', 'fa fa-file-pdf-o');

INSERT INTO icons(name, cssclass)
    VALUES ('ban', 'fa fa-ban');

INSERT INTO icons(name, cssclass)
    VALUES ('tree', 'fa fa-tree');

INSERT INTO icons(name, cssclass)
    VALUES ('angle-double-down', 'fa fa-angle-double-down');

INSERT INTO icons(name, cssclass)
    VALUES ('connectdevelop', 'fa fa-connectdevelop');

INSERT INTO icons(name, cssclass)
    VALUES ('toggle-up', 'fa fa-toggle-up');

INSERT INTO icons(name, cssclass)
    VALUES ('bell', 'fa fa-bell');

INSERT INTO icons(name, cssclass)
    VALUES ('magic', 'fa fa-magic');

INSERT INTO icons(name, cssclass)
    VALUES ('video-camera', 'fa fa-video-camera');

INSERT INTO icons(name, cssclass)
    VALUES ('jsfiddle', 'fa fa-jsfiddle');

INSERT INTO icons(name, cssclass)
    VALUES ('vk', 'fa fa-vk');

INSERT INTO icons(name, cssclass)
    VALUES ('tint', 'fa fa-tint');

INSERT INTO icons(name, cssclass)
    VALUES ('photo', 'fa fa-photo');

INSERT INTO icons(name, cssclass)
    VALUES ('plus', 'fa fa-plus');

INSERT INTO icons(name, cssclass)
    VALUES ('bus', 'fa fa-bus');

INSERT INTO icons(name, cssclass)
    VALUES ('venus-double', 'fa fa-venus-double');

INSERT INTO icons(name, cssclass)
    VALUES ('star-half-o', 'fa fa-star-half-o');

INSERT INTO icons(name, cssclass)
    VALUES ('download', 'fa fa-download');

INSERT INTO icons(name, cssclass)
    VALUES ('skype', 'fa fa-skype');

INSERT INTO icons(name, cssclass)
    VALUES ('credit-card', 'fa fa-credit-card');

INSERT INTO icons(name, cssclass)
    VALUES ('angle-double-right', 'fa fa-angle-double-right');

INSERT INTO icons(name, cssclass)
    VALUES ('square', 'fa fa-square');

INSERT INTO icons(name, cssclass)
    VALUES ('cog', 'fa fa-cog');

INSERT INTO icons(name, cssclass)
    VALUES ('list-alt', 'fa fa-list-alt');

INSERT INTO icons(name, cssclass)
    VALUES ('arrows-alt', 'fa fa-arrows-alt');

INSERT INTO icons(name, cssclass)
    VALUES ('gbp', 'fa fa-gbp');

INSERT INTO icons(name, cssclass)
    VALUES ('minus-square', 'fa fa-minus-square');

INSERT INTO icons(name, cssclass)
    VALUES ('bullseye', 'fa fa-bullseye');

INSERT INTO icons(name, cssclass)
    VALUES ('viacoin', 'fa fa-viacoin');

INSERT INTO icons(name, cssclass)
    VALUES ('caret-square-o-down', 'fa fa-caret-square-o-down');

INSERT INTO icons(name, cssclass)
    VALUES ('angle-right', 'fa fa-angle-right');

INSERT INTO icons(name, cssclass)
    VALUES ('money', 'fa fa-money');

INSERT INTO icons(name, cssclass)
    VALUES ('cc-visa', 'fa fa-cc-visa');

INSERT INTO icons(name, cssclass)
    VALUES ('info', 'fa fa-info');

INSERT INTO icons(name, cssclass)
    VALUES ('toggle-left', 'fa fa-toggle-left');

INSERT INTO icons(name, cssclass)
    VALUES ('flag-checkered', 'fa fa-flag-checkered');

INSERT INTO icons(name, cssclass)
    VALUES ('qq', 'fa fa-qq');

INSERT INTO icons(name, cssclass)
    VALUES ('cloud', 'fa fa-cloud');

INSERT INTO icons(name, cssclass)
    VALUES ('sliders', 'fa fa-sliders');

INSERT INTO icons(name, cssclass)
    VALUES ('envelope', 'fa fa-envelope');

INSERT INTO icons(name, cssclass)
    VALUES ('lemon-o', 'fa fa-lemon-o');

INSERT INTO icons(name, cssclass)
    VALUES ('tty', 'fa fa-tty');

INSERT INTO icons(name, cssclass)
    VALUES ('anchor', 'fa fa-anchor');

INSERT INTO icons(name, cssclass)
    VALUES ('eject', 'fa fa-eject');

INSERT INTO icons(name, cssclass)
    VALUES ('home', 'fa fa-home');

INSERT INTO icons(name, cssclass)
    VALUES ('life-saver', 'fa fa-life-saver');

INSERT INTO icons(name, cssclass)
    VALUES ('rotate-left', 'fa fa-rotate-left');

INSERT INTO icons(name, cssclass)
    VALUES ('square-o', 'fa fa-square-o');

INSERT INTO icons(name, cssclass)
    VALUES ('location-arrow', 'fa fa-location-arrow');

INSERT INTO icons(name, cssclass)
    VALUES ('question-circle', 'fa fa-question-circle');

INSERT INTO icons(name, cssclass)
    VALUES ('header', 'fa fa-header');

INSERT INTO icons(name, cssclass)
    VALUES ('ge', 'fa fa-ge');

INSERT INTO icons(name, cssclass)
    VALUES ('briefcase', 'fa fa-briefcase');

INSERT INTO icons(name, cssclass)
    VALUES ('close', 'fa fa-close');

INSERT INTO icons(name, cssclass)
    VALUES ('hand-o-down', 'fa fa-hand-o-down');

INSERT INTO icons(name, cssclass)
    VALUES ('stethoscope', 'fa fa-stethoscope');

INSERT INTO icons(name, cssclass)
    VALUES ('xing-square', 'fa fa-xing-square');

INSERT INTO icons(name, cssclass)
    VALUES ('mars-double', 'fa fa-mars-double');

INSERT INTO icons(name, cssclass)
    VALUES ('rouble', 'fa fa-rouble');

INSERT INTO icons(name, cssclass)
    VALUES ('mortar-board', 'fa fa-mortar-board');

INSERT INTO icons(name, cssclass)
    VALUES ('clipboard', 'fa fa-clipboard');

INSERT INTO icons(name, cssclass)
    VALUES ('male', 'fa fa-male');

INSERT INTO icons(name, cssclass)
    VALUES ('euro', 'fa fa-euro');

INSERT INTO icons(name, cssclass)
    VALUES ('file-image-o', 'fa fa-file-image-o');

INSERT INTO icons(name, cssclass)
    VALUES ('weibo', 'fa fa-weibo');

INSERT INTO icons(name, cssclass)
    VALUES ('sort-alpha-desc', 'fa fa-sort-alpha-desc');

INSERT INTO icons(name, cssclass)
    VALUES ('reddit', 'fa fa-reddit');

INSERT INTO icons(name, cssclass)
    VALUES ('flag-o', 'fa fa-flag-o');

INSERT INTO icons(name, cssclass)
    VALUES ('automobile', 'fa fa-automobile');

INSERT INTO icons(name, cssclass)
    VALUES ('floppy-o', 'fa fa-floppy-o');

INSERT INTO icons(name, cssclass)
    VALUES ('magnet', 'fa fa-magnet');

INSERT INTO icons(name, cssclass)
    VALUES ('soundcloud', 'fa fa-soundcloud');

INSERT INTO icons(name, cssclass)
    VALUES ('copy', 'fa fa-copy');

INSERT INTO icons(name, cssclass)
    VALUES ('reddit-square', 'fa fa-reddit-square');

INSERT INTO icons(name, cssclass)
    VALUES ('flickr', 'fa fa-flickr');

INSERT INTO icons(name, cssclass)
    VALUES ('minus', 'fa fa-minus');

INSERT INTO icons(name, cssclass)
    VALUES ('cloud-download', 'fa fa-cloud-download');

INSERT INTO icons(name, cssclass)
    VALUES ('link', 'fa fa-link');

INSERT INTO icons(name, cssclass)
    VALUES ('eye-slash', 'fa fa-eye-slash');

INSERT INTO icons(name, cssclass)
    VALUES ('eyedropper', 'fa fa-eyedropper');

INSERT INTO icons(name, cssclass)
    VALUES ('thumbs-o-up', 'fa fa-thumbs-o-up');

INSERT INTO icons(name, cssclass)
    VALUES ('tags', 'fa fa-tags');

INSERT INTO icons(name, cssclass)
    VALUES ('scissors', 'fa fa-scissors');

INSERT INTO icons(name, cssclass)
    VALUES ('chevron-right', 'fa fa-chevron-right');

INSERT INTO icons(name, cssclass)
    VALUES ('times', 'fa fa-times');

INSERT INTO icons(name, cssclass)
    VALUES ('sun-o', 'fa fa-sun-o');

INSERT INTO icons(name, cssclass)
    VALUES ('paperclip', 'fa fa-paperclip');

INSERT INTO icons(name, cssclass)
    VALUES ('unsorted', 'fa fa-unsorted');

INSERT INTO icons(name, cssclass)
    VALUES ('diamond', 'fa fa-diamond');

INSERT INTO icons(name, cssclass)
    VALUES ('google-plus-square', 'fa fa-google-plus-square');

INSERT INTO icons(name, cssclass)
    VALUES ('spoon', 'fa fa-spoon');

INSERT INTO icons(name, cssclass)
    VALUES ('digg', 'fa fa-digg');

INSERT INTO icons(name, cssclass)
    VALUES ('bitbucket', 'fa fa-bitbucket');

INSERT INTO icons(name, cssclass)
    VALUES ('yahoo', 'fa fa-yahoo');

INSERT INTO icons(name, cssclass)
    VALUES ('building-o', 'fa fa-building-o');

INSERT INTO icons(name, cssclass)
    VALUES ('transgender', 'fa fa-transgender');

INSERT INTO icons(name, cssclass)
    VALUES ('bomb', 'fa fa-bomb');

INSERT INTO icons(name, cssclass)
    VALUES ('glass', 'fa fa-glass');

INSERT INTO icons(name, cssclass)
    VALUES ('gamepad', 'fa fa-gamepad');

INSERT INTO icons(name, cssclass)
    VALUES ('futbol-o', 'fa fa-futbol-o');

INSERT INTO icons(name, cssclass)
    VALUES ('youtube', 'fa fa-youtube');

INSERT INTO icons(name, cssclass)
    VALUES ('paper-plane-o', 'fa fa-paper-plane-o');

INSERT INTO icons(name, cssclass)
    VALUES ('hacker-news', 'fa fa-hacker-news');

INSERT INTO icons(name, cssclass)
    VALUES ('coffee', 'fa fa-coffee');

INSERT INTO icons(name, cssclass)
    VALUES ('tablet', 'fa fa-tablet');

INSERT INTO icons(name, cssclass)
    VALUES ('yen', 'fa fa-yen');

INSERT INTO icons(name, cssclass)
    VALUES ('send', 'fa fa-send');

INSERT INTO icons(name, cssclass)
    VALUES ('exclamation-triangle', 'fa fa-exclamation-triangle');

INSERT INTO icons(name, cssclass)
    VALUES ('upload', 'fa fa-upload');

INSERT INTO icons(name, cssclass)
    VALUES ('stack-overflow', 'fa fa-stack-overflow');

INSERT INTO icons(name, cssclass)
    VALUES ('tag', 'fa fa-tag');

INSERT INTO icons(name, cssclass)
    VALUES ('steam', 'fa fa-steam');

INSERT INTO icons(name, cssclass)
    VALUES ('at', 'fa fa-at');

INSERT INTO icons(name, cssclass)
    VALUES ('ticket', 'fa fa-ticket');

INSERT INTO icons(name, cssclass)
    VALUES ('exclamation', 'fa fa-exclamation');

INSERT INTO icons(name, cssclass)
    VALUES ('life-ring', 'fa fa-life-ring');

INSERT INTO icons(name, cssclass)
    VALUES ('dollar', 'fa fa-dollar');

INSERT INTO icons(name, cssclass)
    VALUES ('file-zip-o', 'fa fa-file-zip-o');

INSERT INTO icons(name, cssclass)
    VALUES ('eur', 'fa fa-eur');

INSERT INTO icons(name, cssclass)
    VALUES ('cogs', 'fa fa-cogs');

INSERT INTO icons(name, cssclass)
    VALUES ('exchange', 'fa fa-exchange');

INSERT INTO icons(name, cssclass)
    VALUES ('barcode', 'fa fa-barcode');

INSERT INTO icons(name, cssclass)
    VALUES ('check-circle-o', 'fa fa-check-circle-o');

INSERT INTO icons(name, cssclass)
    VALUES ('code', 'fa fa-code');

INSERT INTO icons(name, cssclass)
    VALUES ('fax', 'fa fa-fax');

INSERT INTO icons(name, cssclass)
    VALUES ('mobile-phone', 'fa fa-mobile-phone');

INSERT INTO icons(name, cssclass)
    VALUES ('hand-o-right', 'fa fa-hand-o-right');

INSERT INTO icons(name, cssclass)
    VALUES ('female', 'fa fa-female');

INSERT INTO icons(name, cssclass)
    VALUES ('search-plus', 'fa fa-search-plus');

INSERT INTO icons(name, cssclass)
    VALUES ('caret-square-o-up', 'fa fa-caret-square-o-up');

INSERT INTO icons(name, cssclass)
    VALUES ('sitemap', 'fa fa-sitemap');

INSERT INTO icons(name, cssclass)
    VALUES ('chevron-circle-down', 'fa fa-chevron-circle-down');

INSERT INTO icons(name, cssclass)
    VALUES ('dropbox', 'fa fa-dropbox');

INSERT INTO icons(name, cssclass)
    VALUES ('thumbs-o-down', 'fa fa-thumbs-o-down');

INSERT INTO icons(name, cssclass)
    VALUES ('plug', 'fa fa-plug');

INSERT INTO icons(name, cssclass)
    VALUES ('angle-down', 'fa fa-angle-down');

INSERT INTO icons(name, cssclass)
    VALUES ('power-off', 'fa fa-power-off');

INSERT INTO icons(name, cssclass)
    VALUES ('gear', 'fa fa-gear');

INSERT INTO icons(name, cssclass)
    VALUES ('linkedin', 'fa fa-linkedin');

INSERT INTO icons(name, cssclass)
    VALUES ('forumbee', 'fa fa-forumbee');

INSERT INTO icons(name, cssclass)
    VALUES ('refresh', 'fa fa-refresh');

INSERT INTO icons(name, cssclass)
    VALUES ('shield', 'fa fa-shield');

INSERT INTO icons(name, cssclass)
    VALUES ('chevron-down', 'fa fa-chevron-down');

INSERT INTO icons(name, cssclass)
    VALUES ('user-secret', 'fa fa-user-secret');

INSERT INTO icons(name, cssclass)
    VALUES ('reply-all', 'fa fa-reply-all');

INSERT INTO icons(name, cssclass)
    VALUES ('sign-in', 'fa fa-sign-in');

INSERT INTO icons(name, cssclass)
    VALUES ('won', 'fa fa-won');

INSERT INTO icons(name, cssclass)
    VALUES ('leaf', 'fa fa-leaf');

INSERT INTO icons(name, cssclass)
    VALUES ('foursquare', 'fa fa-foursquare');

INSERT INTO icons(name, cssclass)
    VALUES ('yelp', 'fa fa-yelp');

INSERT INTO icons(name, cssclass)
    VALUES ('arrow-up', 'fa fa-arrow-up');

INSERT INTO icons(name, cssclass)
    VALUES ('cc-paypal', 'fa fa-cc-paypal');

INSERT INTO icons(name, cssclass)
    VALUES ('sheqel', 'fa fa-sheqel');

INSERT INTO icons(name, cssclass)
    VALUES ('strikethrough', 'fa fa-strikethrough');

INSERT INTO icons(name, cssclass)
    VALUES ('ship', 'fa fa-ship');

INSERT INTO icons(name, cssclass)
    VALUES ('twitter-square', 'fa fa-twitter-square');

INSERT INTO icons(name, cssclass)
    VALUES ('transgender-alt', 'fa fa-transgender-alt');

INSERT INTO icons(name, cssclass)
    VALUES ('toggle-down', 'fa fa-toggle-down');

INSERT INTO icons(name, cssclass)
    VALUES ('long-arrow-right', 'fa fa-long-arrow-right');

INSERT INTO icons(name, cssclass)
    VALUES ('linux', 'fa fa-linux');

INSERT INTO icons(name, cssclass)
    VALUES ('mail-reply', 'fa fa-mail-reply');

INSERT INTO icons(name, cssclass)
    VALUES ('ils', 'fa fa-ils');

INSERT INTO icons(name, cssclass)
    VALUES ('clock-o', 'fa fa-clock-o');

INSERT INTO icons(name, cssclass)
    VALUES ('gift', 'fa fa-gift');

INSERT INTO icons(name, cssclass)
    VALUES ('pie-chart', 'fa fa-pie-chart');

INSERT INTO icons(name, cssclass)
    VALUES ('chevron-up', 'fa fa-chevron-up');

INSERT INTO icons(name, cssclass)
    VALUES ('laptop', 'fa fa-laptop');

INSERT INTO icons(name, cssclass)
    VALUES ('pied-piper-alt', 'fa fa-pied-piper-alt');

INSERT INTO icons(name, cssclass)
    VALUES ('qrcode', 'fa fa-qrcode');

INSERT INTO icons(name, cssclass)
    VALUES ('dashboard', 'fa fa-dashboard');

INSERT INTO icons(name, cssclass)
    VALUES ('crosshairs', 'fa fa-crosshairs');

INSERT INTO icons(name, cssclass)
    VALUES ('chain-broken', 'fa fa-chain-broken');

INSERT INTO icons(name, cssclass)
    VALUES ('hospital-o', 'fa fa-hospital-o');

INSERT INTO icons(name, cssclass)
    VALUES ('shirtsinbulk', 'fa fa-shirtsinbulk');

INSERT INTO icons(name, cssclass)
    VALUES ('cc-discover', 'fa fa-cc-discover');

INSERT INTO icons(name, cssclass)
    VALUES ('indent', 'fa fa-indent');

INSERT INTO icons(name, cssclass)
    VALUES ('arrow-circle-left', 'fa fa-arrow-circle-left');

INSERT INTO icons(name, cssclass)
    VALUES ('bar-chart-o', 'fa fa-bar-chart-o');

INSERT INTO icons(name, cssclass)
    VALUES ('motorcycle', 'fa fa-motorcycle');

INSERT INTO icons(name, cssclass)
    VALUES ('flag', 'fa fa-flag');

INSERT INTO icons(name, cssclass)
    VALUES ('check-square-o', 'fa fa-check-square-o');

INSERT INTO icons(name, cssclass)
    VALUES ('road', 'fa fa-road');

INSERT INTO icons(name, cssclass)
    VALUES ('area-chart', 'fa fa-area-chart');

INSERT INTO icons(name, cssclass)
    VALUES ('sort-alpha-asc', 'fa fa-sort-alpha-asc');

INSERT INTO icons(name, cssclass)
    VALUES ('sort-amount-desc', 'fa fa-sort-amount-desc');

INSERT INTO icons(name, cssclass)
    VALUES ('pencil-square-o', 'fa fa-pencil-square-o');

INSERT INTO icons(name, cssclass)
    VALUES ('volume-down', 'fa fa-volume-down');

INSERT INTO icons(name, cssclass)
    VALUES ('superscript', 'fa fa-superscript');

INSERT INTO icons(name, cssclass)
    VALUES ('warning', 'fa fa-warning');

INSERT INTO icons(name, cssclass)
    VALUES ('keyboard-o', 'fa fa-keyboard-o');

INSERT INTO icons(name, cssclass)
    VALUES ('genderless', 'fa fa-genderless');

INSERT INTO icons(name, cssclass)
    VALUES ('google-wallet', 'fa fa-google-wallet');

INSERT INTO icons(name, cssclass)
    VALUES ('volume-up', 'fa fa-volume-up');

INSERT INTO icons(name, cssclass)
    VALUES ('codepen', 'fa fa-codepen');

INSERT INTO icons(name, cssclass)
    VALUES ('th', 'fa fa-th');

INSERT INTO icons(name, cssclass)
    VALUES ('file-code-o', 'fa fa-file-code-o');

INSERT INTO icons(name, cssclass)
    VALUES ('facebook-square', 'fa fa-facebook-square');

INSERT INTO icons(name, cssclass)
    VALUES ('plus-circle', 'fa fa-plus-circle');

INSERT INTO icons(name, cssclass)
    VALUES ('pinterest-p', 'fa fa-pinterest-p');

INSERT INTO icons(name, cssclass)
    VALUES ('rmb', 'fa fa-rmb');

INSERT INTO icons(name, cssclass)
    VALUES ('paste', 'fa fa-paste');

INSERT INTO icons(name, cssclass)
    VALUES ('pagelines', 'fa fa-pagelines');

INSERT INTO icons(name, cssclass)
    VALUES ('plus-square-o', 'fa fa-plus-square-o');

INSERT INTO icons(name, cssclass)
    VALUES ('building', 'fa fa-building');

INSERT INTO icons(name, cssclass)
    VALUES ('chain', 'fa fa-chain');

INSERT INTO icons(name, cssclass)
    VALUES ('mars-stroke', 'fa fa-mars-stroke');

INSERT INTO icons(name, cssclass)
    VALUES ('ambulance', 'fa fa-ambulance');

INSERT INTO icons(name, cssclass)
    VALUES ('step-forward', 'fa fa-step-forward');

INSERT INTO icons(name, cssclass)
    VALUES ('pied-piper', 'fa fa-pied-piper');

INSERT INTO icons(name, cssclass)
    VALUES ('github-square', 'fa fa-github-square');

INSERT INTO icons(name, cssclass)
    VALUES ('bed', 'fa fa-bed');

INSERT INTO icons(name, cssclass)
    VALUES ('medkit', 'fa fa-medkit');

INSERT INTO icons(name, cssclass)
    VALUES ('sort-up', 'fa fa-sort-up');

INSERT INTO icons(name, cssclass)
    VALUES ('folder-o', 'fa fa-folder-o');

INSERT INTO icons(name, cssclass)
    VALUES ('dedent', 'fa fa-dedent');

INSERT INTO icons(name, cssclass)
    VALUES ('code-fork', 'fa fa-code-fork');

INSERT INTO icons(name, cssclass)
    VALUES ('life-buoy', 'fa fa-life-buoy');

INSERT INTO icons(name, cssclass)
    VALUES ('compress', 'fa fa-compress');

INSERT INTO icons(name, cssclass)
    VALUES ('folder', 'fa fa-folder');

INSERT INTO icons(name, cssclass)
    VALUES ('cut', 'fa fa-cut');

INSERT INTO icons(name, cssclass)
    VALUES ('venus', 'fa fa-venus');

INSERT INTO icons(name, cssclass)
    VALUES ('circle-o-notch', 'fa fa-circle-o-notch');

INSERT INTO icons(name, cssclass)
    VALUES ('gears', 'fa fa-gears');

INSERT INTO icons(name, cssclass)
    VALUES ('mars-stroke-h', 'fa fa-mars-stroke-h');

INSERT INTO icons(name, cssclass)
    VALUES ('film', 'fa fa-film');

INSERT INTO icons(name, cssclass)
    VALUES ('files-o', 'fa fa-files-o');

INSERT INTO icons(name, cssclass)
    VALUES ('align-center', 'fa fa-align-center');

INSERT INTO icons(name, cssclass)
    VALUES ('arrows', 'fa fa-arrows');

INSERT INTO icons(name, cssclass)
    VALUES ('cubes', 'fa fa-cubes');

INSERT INTO icons(name, cssclass)
    VALUES ('inr', 'fa fa-inr');

INSERT INTO icons(name, cssclass)
    VALUES ('cutlery', 'fa fa-cutlery');

INSERT INTO icons(name, cssclass)
    VALUES ('users', 'fa fa-users');

INSERT INTO icons(name, cssclass)
    VALUES ('rss-square', 'fa fa-rss-square');

INSERT INTO icons(name, cssclass)
    VALUES ('arrow-down', 'fa fa-arrow-down');

INSERT INTO icons(name, cssclass)
    VALUES ('share', 'fa fa-share');

INSERT INTO icons(name, cssclass)
    VALUES ('history', 'fa fa-history');

INSERT INTO icons(name, cssclass)
    VALUES ('times-circle', 'fa fa-times-circle');

INSERT INTO icons(name, cssclass)
    VALUES ('joomla', 'fa fa-joomla');

INSERT INTO icons(name, cssclass)
    VALUES ('arrows-v', 'fa fa-arrows-v');

INSERT INTO icons(name, cssclass)
    VALUES ('slideshare', 'fa fa-slideshare');

INSERT INTO icons(name, cssclass)
    VALUES ('list', 'fa fa-list');

INSERT INTO icons(name, cssclass)
    VALUES ('file-text', 'fa fa-file-text');

INSERT INTO icons(name, cssclass)
    VALUES ('linkedin-square', 'fa fa-linkedin-square');

INSERT INTO icons(name, cssclass)
    VALUES ('medium', 'fa fa-medium');

INSERT INTO icons(name, cssclass)
    VALUES ('android', 'fa fa-android');

INSERT INTO icons(name, cssclass)
    VALUES ('paragraph', 'fa fa-paragraph');

INSERT INTO icons(name, cssclass)
    VALUES ('pinterest-square', 'fa fa-pinterest-square');

INSERT INTO icons(name, cssclass)
    VALUES ('ellipsis-h', 'fa fa-ellipsis-h');

INSERT INTO icons(name, cssclass)
    VALUES ('bell-o', 'fa fa-bell-o');

INSERT INTO icons(name, cssclass)
    VALUES ('shopping-cart', 'fa fa-shopping-cart');

INSERT INTO icons(name, cssclass)
    VALUES ('thumb-tack', 'fa fa-thumb-tack');

INSERT INTO icons(name, cssclass)
    VALUES ('globe', 'fa fa-globe');

INSERT INTO icons(name, cssclass)
    VALUES ('subscript', 'fa fa-subscript');

INSERT INTO icons(name, cssclass)
    VALUES ('bicycle', 'fa fa-bicycle');

INSERT INTO icons(name, cssclass)
    VALUES ('file-text-o', 'fa fa-file-text-o');

INSERT INTO icons(name, cssclass)
    VALUES ('pause', 'fa fa-pause');

INSERT INTO icons(name, cssclass)
    VALUES ('chevron-circle-right', 'fa fa-chevron-circle-right');

INSERT INTO icons(name, cssclass)
    VALUES ('car', 'fa fa-car');

INSERT INTO icons(name, cssclass)
    VALUES ('taxi', 'fa fa-taxi');

INSERT INTO icons(name, cssclass)
    VALUES ('twitter', 'fa fa-twitter');

INSERT INTO icons(name, cssclass)
    VALUES ('h-square', 'fa fa-h-square');

INSERT INTO icons(name, cssclass)
    VALUES ('mail-forward', 'fa fa-mail-forward');

INSERT INTO icons(name, cssclass)
    VALUES ('bookmark-o', 'fa fa-bookmark-o');

INSERT INTO icons(name, cssclass)
    VALUES ('fire-extinguisher', 'fa fa-fire-extinguisher');



INSERT INTO functions(functionid, modulename, classname, functiontype, name, description, defaultconfig, component)
    VALUES ('60000000-0000-0000-0000-000000000000', 'local_file_storage.py', 'LocalFileStorageFunction', 'node', 'Local File Upload', 'Sets the default storage mechanism for uploaded files', '{}', 'views/components/functions/local-file-storage');

INSERT INTO functions(functionid, modulename, classname, functiontype, name, description, defaultconfig, component)
    VALUES ('60000000-0000-0000-0000-000000000001', 'primary_descriptors.py', 'PrimaryDescriptorsFunction', 'primarydescriptors', 'Define Resource Descriptors', 'Configure the name, description, and map popup of a resource', '{"module": "arches.app.functions.primary_descriptors", "class_name":"PrimaryDescriptorsFunction", "descriptor_types": {"name": {"nodegroup_id": "", "string_template": ""}, "description": {"nodegroup_id": "", "string_template":""}, "map_popup": {"nodegroup_id": "", "string_template":""}} }', 'views/components/functions/primary-descriptors');

INSERT INTO functions(functionid, modulename, classname, functiontype, name, description, defaultconfig, component)
    VALUES ('60000000-0000-0000-0000-000000000002', 'required_nodes.py', 'RequiredNodesFunction', 'validation', 'Define Required Nodes', 'Define which values are required for a user to save card', '{"required_nodes":"{}"}', 'views/components/functions/required-nodes');

INSERT INTO map_sources(name, source)
    VALUES ('mapbox-streets', '{
        "url": "mapbox://mapbox.mapbox-streets-v8",
        "type": "vector"
    }');

INSERT INTO map_sources(name, source)
    VALUES ('mapbox-satellite', '{
        "type": "raster",
        "url": "mapbox://mapbox.satellite",
        "tileSize": 256
    }');

INSERT INTO map_sources(name, source)
   VALUES ('mapzen', '{
               "type": "vector",
               "tiles": ["https://vector.mapzen.com/osm/all/{z}/{x}/{y}.mvt?api_key=vector-tiles-LM25tq4"]
       }');


INSERT INTO map_sources(name, source)
  VALUES ('geocode-point', '{
      "type": "geojson",
      "data": {
          "type": "FeatureCollection",
          "features": []
      }
  }');

INSERT INTO map_sources(name, source)
VALUES ('search-query', '{
    "type": "geojson",
    "data": {
        "type": "FeatureCollection",
        "features": []
    }
}');

INSERT INTO map_layers(maplayerid, name, layerdefinitions, isoverlay, icon, activated, addtomap)
    VALUES (public.uuid_generate_v1mc(), 'satellite', '[{
        "id": "satellite",
        "type": "raster",
        "source": "mapbox-satellite",
        "source-layer": "mapbox_satellite_full"
    }]', FALSE, '', TRUE, FALSE);

INSERT INTO map_layers(maplayerid, name, layerdefinitions, isoverlay, icon, activated, addtomap)
    VALUES (public.uuid_generate_v1mc(), 'streets', '[
        {
            "id": "land",
            "type": "background",
            "metadata": {
                "mapbox:featureComponent": "land-and-water",
                "mapbox:group": "Land, water, & sky, land"
            },
            "layout": {},
            "paint": {"background-color": "hsl(40, 46%, 86%)"}
        },
        {
            "id": "national-park",
            "type": "fill",
            "metadata": {
                "mapbox:featureComponent": "land-and-water",
                "mapbox:group": "Land, water, & sky, land"
            },
            "source": "mapbox-streets",
            "source-layer": "landuse_overlay",
            "minzoom": 5,
            "filter": ["==", ["get", "class"], "national_park"],
            "layout": {},
            "paint": {
                "fill-color": "hsl(78, 50%, 73%)",
                "fill-opacity": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    5,
                    0,
                    6,
                    0.5,
                    10,
                    0.5
                ]
            }
        },
        {
            "id": "landuse",
            "type": "fill",
            "metadata": {
                "mapbox:featureComponent": "land-and-water",
                "mapbox:group": "Land, water, & sky, land"
            },
            "source": "mapbox-streets",
            "source-layer": "landuse",
            "minzoom": 5,
            "filter": [
                "match",
                ["get", "class"],
                ["park", "airport", "glacier", "pitch", "sand", "facility"],
                true,
                "cemetery",
                true,
                "school",
                true,
                "hospital",
                true,
                false
            ],
            "layout": {},
            "paint": {
                "fill-color": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    15,
                    [
                        "match",
                        ["get", "class"],
                        "park",
                        "hsl(78, 50%, 73%)",
                        "airport",
                        "hsl(225, 49%, 88%)",
                        "cemetery",
                        "hsl(60, 49%, 79%)",
                        "glacier",
                        "hsl(205, 56%, 88%)",
                        "hospital",
                        "hsl(3, 47%, 84%)",
                        "pitch",
                        "hsl(78, 51%, 68%)",
                        "sand",
                        "hsl(43, 50%, 83%)",
                        "school",
                        "hsl(40, 47%, 78%)",
                        "hsl(40, 49%, 82%)"
                    ],
                    16,
                    [
                        "match",
                        ["get", "class"],
                        "park",
                        "hsl(78, 50%, 73%)",
                        "airport",
                        "hsl(225, 63%, 86%)",
                        "cemetery",
                        "hsl(60, 49%, 79%)",
                        "glacier",
                        "hsl(205, 56%, 88%)",
                        "hospital",
                        "hsl(3, 46%, 86%)",
                        "pitch",
                        "hsl(78, 51%, 68%)",
                        "sand",
                        "hsl(43, 50%, 83%)",
                        "school",
                        "hsl(40, 47%, 78%)",
                        "hsl(40, 49%, 82%)"
                    ]
                ],
                "fill-opacity": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    5,
                    0,
                    6,
                    ["match", ["get", "class"], "glacier", 0.5, 1]
                ]
            }
        },
        {
            "id": "pitch-outline",
            "type": "line",
            "metadata": {
                "mapbox:featureComponent": "land-and-water",
                "mapbox:group": "Land, water, & sky, land"
            },
            "source": "mapbox-streets",
            "source-layer": "landuse",
            "minzoom": 15,
            "filter": ["==", ["get", "class"], "pitch"],
            "layout": {},
            "paint": {"line-color": "hsl(60, 29%, 81%)"}
        },
        {
            "id": "waterway",
            "type": "line",
            "metadata": {
                "mapbox:featureComponent": "land-and-water",
                "mapbox:group": "Land, water, & sky, water"
            },
            "source": "mapbox-streets",
            "source-layer": "waterway",
            "minzoom": 8,
            "layout": {
                "line-cap": ["step", ["zoom"], "butt", 11, "round"],
                "line-join": "round"
            },
            "paint": {
                "line-color": "hsl(205, 76%, 70%)",
                "line-width": [
                    "interpolate",
                    ["exponential", 1.3],
                    ["zoom"],
                    9,
                    ["match", ["get", "class"], ["canal", "river"], 0.1, 0],
                    20,
                    ["match", ["get", "class"], ["canal", "river"], 8, 3]
                ],
                "line-opacity": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    8,
                    0,
                    8.5,
                    1
                ]
            }
        },
        {
            "id": "water",
            "type": "fill",
            "metadata": {
                "mapbox:featureComponent": "land-and-water",
                "mapbox:group": "Land, water, & sky, water"
            },
            "source": "mapbox-streets",
            "source-layer": "water",
            "layout": {},
            "paint": {"fill-color": "hsl(205, 76%, 70%)"}
        },
        {
            "id": "land-structure-polygon",
            "type": "fill",
            "metadata": {
                "mapbox:featureComponent": "land-and-water",
                "mapbox:group": "Land, water, & sky, built"
            },
            "source": "mapbox-streets",
            "source-layer": "structure",
            "minzoom": 13,
            "filter": [
                "all",
                ["==", ["geometry-type"], "Polygon"],
                ["==", ["get", "class"], "land"]
            ],
            "layout": {},
            "paint": {"fill-color": "hsl(40, 46%, 86%)"}
        },
        {
            "id": "land-structure-line",
            "type": "line",
            "metadata": {
                "mapbox:featureComponent": "land-and-water",
                "mapbox:group": "Land, water, & sky, built"
            },
            "source": "mapbox-streets",
            "source-layer": "structure",
            "minzoom": 13,
            "filter": [
                "all",
                ["==", ["geometry-type"], "LineString"],
                ["==", ["get", "class"], "land"]
            ],
            "layout": {"line-cap": "round"},
            "paint": {
                "line-width": [
                    "interpolate",
                    ["exponential", 1.99],
                    ["zoom"],
                    14,
                    0.75,
                    20,
                    40
                ],
                "line-color": "hsl(40, 46%, 86%)"
            }
        },
        {
            "id": "aeroway-polygon",
            "type": "fill",
            "metadata": {
                "mapbox:featureComponent": "transit",
                "mapbox:group": "Transit, built"
            },
            "source": "mapbox-streets",
            "source-layer": "aeroway",
            "minzoom": 11,
            "filter": [
                "all",
                ["==", ["geometry-type"], "Polygon"],
                [
                    "match",
                    ["get", "type"],
                    ["runway", "taxiway", "helipad"],
                    true,
                    false
                ]
            ],
            "layout": {},
            "paint": {
                "fill-color": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    15,
                    "hsl(225, 37%, 79%)",
                    16,
                    "hsl(225, 19%, 81%)"
                ],
                "fill-opacity": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    11,
                    0,
                    11.5,
                    1
                ]
            }
        },
        {
            "id": "aeroway-line",
            "type": "line",
            "metadata": {
                "mapbox:featureComponent": "transit",
                "mapbox:group": "Transit, built"
            },
            "source": "mapbox-streets",
            "source-layer": "aeroway",
            "minzoom": 9,
            "filter": ["==", ["geometry-type"], "LineString"],
            "layout": {},
            "paint": {
                "line-color": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    15,
                    "hsl(225, 37%, 79%)",
                    16,
                    "hsl(225, 19%, 81%)"
                ],
                "line-width": [
                    "interpolate",
                    ["exponential", 1.5],
                    ["zoom"],
                    9,
                    ["match", ["get", "type"], "runway", 1, 0.5],
                    18,
                    ["match", ["get", "type"], "runway", 80, 20]
                ]
            }
        },
        {
            "id": "building-outline",
            "type": "line",
            "metadata": {
                "mapbox:featureComponent": "buildings",
                "mapbox:group": "Buildings, built"
            },
            "source": "mapbox-streets",
            "source-layer": "building",
            "minzoom": 15,
            "filter": [
                "all",
                ["!=", ["get", "type"], "building:part"],
                ["==", ["get", "underground"], "false"]
            ],
            "layout": {},
            "paint": {
                "line-color": "hsl(40, 42%, 77%)",
                "line-width": [
                    "interpolate",
                    ["exponential", 1.5],
                    ["zoom"],
                    15,
                    0.75,
                    20,
                    3
                ],
                "line-opacity": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    15,
                    0,
                    16,
                    1
                ]
            }
        },
        {
            "id": "building",
            "type": "fill",
            "metadata": {
                "mapbox:featureComponent": "buildings",
                "mapbox:group": "Buildings, built"
            },
            "source": "mapbox-streets",
            "source-layer": "building",
            "minzoom": 15,
            "filter": [
                "all",
                ["!=", ["get", "type"], "building:part"],
                ["==", ["get", "underground"], "false"]
            ],
            "layout": {},
            "paint": {
                "fill-color": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    15,
                    "hsl(40, 45%, 83%)",
                    16,
                    "hsl(40, 41%, 82%)"
                ],
                "fill-opacity": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    15,
                    0,
                    16,
                    1
                ],
                "fill-outline-color": "hsl(40, 42%, 77%)"
            }
        },
        {
            "id": "tunnel-path",
            "type": "line",
            "metadata": {
                "mapbox:featureComponent": "walking-cycling",
                "mapbox:group": "Walking, cycling, etc., tunnels"
            },
            "source": "mapbox-streets",
            "source-layer": "road",
            "minzoom": 14,
            "filter": [
                "all",
                ["==", ["get", "structure"], "tunnel"],
                ["==", ["get", "class"], "path"],
                ["!=", ["get", "type"], "steps"],
                ["==", ["geometry-type"], "LineString"]
            ],
            "layout": {},
            "paint": {
                "line-width": [
                    "interpolate",
                    ["exponential", 1.5],
                    ["zoom"],
                    15,
                    1,
                    18,
                    4
                ],
                "line-color": "hsl(40, 42%, 77%)",
                "line-dasharray": [
                    "step",
                    ["zoom"],
                    ["literal", [1, 0]],
                    15,
                    ["literal", [1.75, 1]],
                    16,
                    ["literal", [1, 0.75]],
                    17,
                    ["literal", [1, 0.5]]
                ]
            }
        },
        {
            "id": "tunnel-steps",
            "type": "line",
            "metadata": {
                "mapbox:featureComponent": "walking-cycling",
                "mapbox:group": "Walking, cycling, etc., tunnels"
            },
            "source": "mapbox-streets",
            "source-layer": "road",
            "minzoom": 14,
            "filter": [
                "all",
                ["==", ["get", "structure"], "tunnel"],
                ["==", ["get", "type"], "steps"],
                ["==", ["geometry-type"], "LineString"]
            ],
            "layout": {},
            "paint": {
                "line-width": [
                    "interpolate",
                    ["exponential", 1.5],
                    ["zoom"],
                    15,
                    1,
                    16,
                    1.6,
                    18,
                    6
                ],
                "line-color": "hsl(40, 42%, 77%)",
                "line-dasharray": [
                    "step",
                    ["zoom"],
                    ["literal", [1, 0]],
                    15,
                    ["literal", [1.75, 1]],
                    16,
                    ["literal", [1, 0.75]],
                    17,
                    ["literal", [0.3, 0.3]]
                ]
            }
        },
        {
            "id": "tunnel-pedestrian",
            "type": "line",
            "metadata": {
                "mapbox:featureComponent": "walking-cycling",
                "mapbox:group": "Walking, cycling, etc., tunnels"
            },
            "source": "mapbox-streets",
            "source-layer": "road",
            "minzoom": 13,
            "filter": [
                "all",
                ["==", ["get", "structure"], "tunnel"],
                ["==", ["get", "class"], "pedestrian"],
                ["==", ["geometry-type"], "LineString"]
            ],
            "layout": {},
            "paint": {
                "line-width": [
                    "interpolate",
                    ["exponential", 1.5],
                    ["zoom"],
                    14,
                    0.5,
                    18,
                    12
                ],
                "line-color": "hsl(40, 42%, 77%)",
                "line-dasharray": [
                    "step",
                    ["zoom"],
                    ["literal", [1, 0]],
                    15,
                    ["literal", [1.5, 0.4]],
                    16,
                    ["literal", [1, 0.2]]
                ]
            }
        },
        {
            "id": "tunnel-simple",
            "type": "line",
            "metadata": {
                "mapbox:featureComponent": "road-network",
                "mapbox:group": "Road network, tunnels"
            },
            "source": "mapbox-streets",
            "source-layer": "road",
            "minzoom": 13,
            "filter": [
                "all",
                ["==", ["get", "structure"], "tunnel"],
                [
                    "step",
                    ["zoom"],
                    [
                        "match",
                        ["get", "class"],
                        [
                            "motorway",
                            "motorway_link",
                            "trunk",
                            "trunk_link",
                            "primary",
                            "secondary",
                            "tertiary",
                            "street",
                            "street_limited",
                            "primary_link",
                            "track"
                        ],
                        true,
                        false
                    ],
                    14,
                    [
                        "match",
                        ["get", "class"],
                        [
                            "motorway",
                            "motorway_link",
                            "trunk",
                            "trunk_link",
                            "primary",
                            "primary_link",
                            "secondary",
                            "secondary_link",
                            "tertiary",
                            "tertiary_link",
                            "street",
                            "street_limited",
                            "service",
                            "track"
                        ],
                        true,
                        false
                    ]
                ],
                ["==", ["geometry-type"], "LineString"]
            ],
            "layout": {},
            "paint": {
                "line-width": [
                    "interpolate",
                    ["exponential", 1.5],
                    ["zoom"],
                    13,
                    [
                        "match",
                        ["get", "class"],
                        ["motorway", "trunk", "primary"],
                        4,
                        ["secondary", "tertiary"],
                        2.5,
                        [
                            "motorway_link",
                            "trunk_link",
                            "street",
                            "street_limited",
                            "primary_link"
                        ],
                        1,
                        0.5
                    ],
                    18,
                    [
                        "match",
                        ["get", "class"],
                        ["motorway", "trunk", "primary"],
                        32,
                        ["secondary", "tertiary"],
                        26,
                        [
                            "motorway_link",
                            "trunk_link",
                            "street",
                            "street_limited",
                            "primary_link"
                        ],
                        18,
                        12
                    ]
                ],
                "line-color": "hsl(38, 55%, 93%)"
            }
        },
        {
            "id": "road-path",
            "type": "line",
            "metadata": {
                "mapbox:featureComponent": "walking-cycling",
                "mapbox:group": "Walking, cycling, etc., surface"
            },
            "source": "mapbox-streets",
            "source-layer": "road",
            "minzoom": 12,
            "filter": [
                "all",
                ["==", ["get", "class"], "path"],
                [
                    "step",
                    ["zoom"],
                    [
                        "!",
                        [
                            "match",
                            ["get", "type"],
                            ["steps", "sidewalk", "crossing"],
                            true,
                            false
                        ]
                    ],
                    16,
                    ["!=", ["get", "type"], "steps"]
                ],
                ["match", ["get", "structure"], ["none", "ford"], true, false],
                ["==", ["geometry-type"], "LineString"]
            ],
            "layout": {"line-join": ["step", ["zoom"], "miter", 14, "round"]},
            "paint": {
                "line-width": [
                    "interpolate",
                    ["exponential", 1.5],
                    ["zoom"],
                    13,
                    0.5,
                    14,
                    1,
                    15,
                    1,
                    18,
                    4
                ],
                "line-color": "hsl(40, 47%, 96%)",
                "line-dasharray": [
                    "step",
                    ["zoom"],
                    ["literal", [4, 0.3]],
                    15,
                    ["literal", [1.75, 0.3]],
                    16,
                    ["literal", [1, 0.3]],
                    17,
                    ["literal", [1, 0.25]]
                ]
            }
        },
        {
            "id": "road-steps",
            "type": "line",
            "metadata": {
                "mapbox:featureComponent": "walking-cycling",
                "mapbox:group": "Walking, cycling, etc., surface"
            },
            "source": "mapbox-streets",
            "source-layer": "road",
            "minzoom": 14,
            "filter": [
                "all",
                ["==", ["get", "type"], "steps"],
                ["match", ["get", "structure"], ["none", "ford"], true, false],
                ["==", ["geometry-type"], "LineString"]
            ],
            "layout": {"line-join": "round"},
            "paint": {
                "line-width": [
                    "interpolate",
                    ["exponential", 1.5],
                    ["zoom"],
                    15,
                    1,
                    16,
                    1.6,
                    18,
                    6
                ],
                "line-color": "hsl(40, 47%, 96%)",
                "line-dasharray": [
                    "step",
                    ["zoom"],
                    ["literal", [1, 0]],
                    15,
                    ["literal", [1.75, 1]],
                    16,
                    ["literal", [1, 0.75]],
                    17,
                    ["literal", [0.3, 0.3]]
                ]
            }
        },
        {
            "id": "road-pedestrian",
            "type": "line",
            "metadata": {
                "mapbox:featureComponent": "walking-cycling",
                "mapbox:group": "Walking, cycling, etc., surface"
            },
            "source": "mapbox-streets",
            "source-layer": "road",
            "minzoom": 12,
            "filter": [
                "all",
                ["==", ["get", "class"], "pedestrian"],
                ["match", ["get", "structure"], ["none", "ford"], true, false],
                ["==", ["geometry-type"], "LineString"]
            ],
            "layout": {"line-join": ["step", ["zoom"], "miter", 14, "round"]},
            "paint": {
                "line-width": [
                    "interpolate",
                    ["exponential", 1.5],
                    ["zoom"],
                    14,
                    0.5,
                    18,
                    12
                ],
                "line-color": "hsl(40, 47%, 96%)",
                "line-dasharray": [
                    "step",
                    ["zoom"],
                    ["literal", [1, 0]],
                    15,
                    ["literal", [1.5, 0.4]],
                    16,
                    ["literal", [1, 0.2]]
                ]
            }
        },
        {
            "id": "road-simple",
            "type": "line",
            "metadata": {
                "mapbox:featureComponent": "road-network",
                "mapbox:group": "Road network, surface"
            },
            "source": "mapbox-streets",
            "source-layer": "road",
            "minzoom": 5,
            "filter": [
                "all",
                [
                    "step",
                    ["zoom"],
                    [
                        "match",
                        ["get", "class"],
                        ["motorway", "trunk"],
                        true,
                        false
                    ],
                    6,
                    [
                        "match",
                        ["get", "class"],
                        ["motorway", "trunk", "primary"],
                        true,
                        false
                    ],
                    8,
                    [
                        "match",
                        ["get", "class"],
                        ["motorway", "trunk", "primary", "secondary"],
                        true,
                        false
                    ],
                    10,
                    [
                        "match",
                        ["get", "class"],
                        [
                            "motorway",
                            "trunk",
                            "primary",
                            "secondary",
                            "tertiary",
                            "motorway_link",
                            "trunk_link"
                        ],
                        true,
                        false
                    ],
                    11,
                    [
                        "match",
                        ["get", "class"],
                        [
                            "motorway",
                            "motorway_link",
                            "trunk",
                            "trunk_link",
                            "primary",
                            "secondary",
                            "tertiary",
                            "street"
                        ],
                        true,
                        false
                    ],
                    12,
                    [
                        "match",
                        ["get", "class"],
                        [
                            "motorway",
                            "motorway_link",
                            "trunk",
                            "trunk_link",
                            "primary",
                            "secondary",
                            "tertiary",
                            "street",
                            "street_limited",
                            "primary_link"
                        ],
                        true,
                        false
                    ],
                    13,
                    [
                        "match",
                        ["get", "class"],
                        [
                            "motorway",
                            "motorway_link",
                            "trunk",
                            "trunk_link",
                            "primary",
                            "secondary",
                            "tertiary",
                            "street",
                            "street_limited",
                            "primary_link",
                            "track"
                        ],
                        true,
                        false
                    ],
                    14,
                    [
                        "match",
                        ["get", "class"],
                        [
                            "motorway",
                            "motorway_link",
                            "trunk",
                            "trunk_link",
                            "primary",
                            "primary_link",
                            "secondary",
                            "secondary_link",
                            "tertiary",
                            "tertiary_link",
                            "street",
                            "street_limited",
                            "service",
                            "track"
                        ],
                        true,
                        false
                    ]
                ],
                ["match", ["get", "structure"], ["none", "ford"], true, false],
                ["==", ["geometry-type"], "LineString"]
            ],
            "layout": {
                "line-cap": ["step", ["zoom"], "butt", 14, "round"],
                "line-join": ["step", ["zoom"], "miter", 14, "round"]
            },
            "paint": {
                "line-width": [
                    "interpolate",
                    ["exponential", 1.5],
                    ["zoom"],
                    5,
                    [
                        "match",
                        ["get", "class"],
                        ["motorway", "trunk", "primary"],
                        0.75,
                        ["secondary", "tertiary"],
                        0.1,
                        0
                    ],
                    13,
                    [
                        "match",
                        ["get", "class"],
                        ["motorway", "trunk", "primary"],
                        4,
                        ["secondary", "tertiary"],
                        2.5,
                        [
                            "motorway_link",
                            "trunk_link",
                            "primary_link",
                            "street",
                            "street_limited"
                        ],
                        1,
                        0.5
                    ],
                    18,
                    [
                        "match",
                        ["get", "class"],
                        ["motorway", "trunk", "primary"],
                        32,
                        ["secondary", "tertiary"],
                        26,
                        [
                            "motorway_link",
                            "trunk_link",
                            "primary_link",
                            "street",
                            "street_limited"
                        ],
                        18,
                        10
                    ]
                ],
                "line-color": [
                    "match",
                    ["get", "class"],
                    [
                        "primary_link",
                        "secondary_link",
                        "tertiary_link",
                        "street",
                        "street_limited",
                        "service",
                        "track"
                    ],
                    "hsl(38, 55%, 97%)",
                    "hsl(38, 55%, 100%)"
                ]
            }
        },
        {
            "id": "bridge-path",
            "type": "line",
            "metadata": {
                "mapbox:featureComponent": "walking-cycling",
                "mapbox:group": "Walking, cycling, etc., barriers-bridges"
            },
            "source": "mapbox-streets",
            "source-layer": "road",
            "minzoom": 14,
            "filter": [
                "all",
                ["==", ["get", "structure"], "bridge"],
                ["==", ["get", "class"], "path"],
                ["==", ["geometry-type"], "LineString"],
                ["!=", ["get", "type"], "steps"]
            ],
            "layout": {"line-join": "round"},
            "paint": {
                "line-width": [
                    "interpolate",
                    ["exponential", 1.5],
                    ["zoom"],
                    15,
                    1,
                    18,
                    4
                ],
                "line-color": "hsl(40, 47%, 96%)",
                "line-dasharray": [
                    "step",
                    ["zoom"],
                    ["literal", [4, 0.3]],
                    15,
                    ["literal", [1.75, 0.3]],
                    16,
                    ["literal", [1, 0.3]],
                    17,
                    ["literal", [1, 0.25]]
                ]
            }
        },
        {
            "id": "bridge-steps",
            "type": "line",
            "metadata": {
                "mapbox:featureComponent": "walking-cycling",
                "mapbox:group": "Walking, cycling, etc., barriers-bridges"
            },
            "source": "mapbox-streets",
            "source-layer": "road",
            "minzoom": 14,
            "filter": [
                "all",
                ["==", ["get", "type"], "steps"],
                ["==", ["get", "structure"], "bridge"],
                ["==", ["geometry-type"], "LineString"]
            ],
            "layout": {"line-join": "round"},
            "paint": {
                "line-width": [
                    "interpolate",
                    ["exponential", 1.5],
                    ["zoom"],
                    15,
                    1,
                    16,
                    1.6,
                    18,
                    6
                ],
                "line-color": "hsl(40, 47%, 96%)",
                "line-dasharray": [
                    "step",
                    ["zoom"],
                    ["literal", [1, 0]],
                    15,
                    ["literal", [1.75, 1]],
                    16,
                    ["literal", [1, 0.75]],
                    17,
                    ["literal", [0.3, 0.3]]
                ]
            }
        },
        {
            "id": "bridge-pedestrian",
            "type": "line",
            "metadata": {
                "mapbox:featureComponent": "walking-cycling",
                "mapbox:group": "Walking, cycling, etc., barriers-bridges"
            },
            "source": "mapbox-streets",
            "source-layer": "road",
            "minzoom": 13,
            "filter": [
                "all",
                ["==", ["get", "structure"], "bridge"],
                ["==", ["get", "class"], "pedestrian"],
                ["==", ["geometry-type"], "LineString"]
            ],
            "layout": {"line-join": "round"},
            "paint": {
                "line-width": [
                    "interpolate",
                    ["exponential", 1.5],
                    ["zoom"],
                    14,
                    0.5,
                    18,
                    12
                ],
                "line-color": "hsl(40, 47%, 96%)",
                "line-dasharray": [
                    "step",
                    ["zoom"],
                    ["literal", [1, 0]],
                    15,
                    ["literal", [1.5, 0.4]],
                    16,
                    ["literal", [1, 0.2]]
                ]
            }
        },
        {
            "id": "bridge-case-simple",
            "type": "line",
            "metadata": {
                "mapbox:featureComponent": "road-network",
                "mapbox:group": "Road network, bridges"
            },
            "source": "mapbox-streets",
            "source-layer": "road",
            "minzoom": 13,
            "filter": [
                "all",
                ["==", ["get", "structure"], "bridge"],
                [
                    "step",
                    ["zoom"],
                    [
                        "match",
                        ["get", "class"],
                        [
                            "motorway",
                            "motorway_link",
                            "trunk",
                            "trunk_link",
                            "primary",
                            "secondary",
                            "tertiary",
                            "street",
                            "street_limited",
                            "primary_link",
                            "track"
                        ],
                        true,
                        false
                    ],
                    14,
                    [
                        "match",
                        ["get", "class"],
                        [
                            "motorway",
                            "motorway_link",
                            "trunk",
                            "trunk_link",
                            "primary",
                            "primary_link",
                            "secondary",
                            "secondary_link",
                            "tertiary",
                            "tertiary_link",
                            "street",
                            "street_limited",
                            "service",
                            "track"
                        ],
                        true,
                        false
                    ]
                ],
                ["==", ["geometry-type"], "LineString"]
            ],
            "layout": {"line-join": ["step", ["zoom"], "miter", 14, "round"]},
            "paint": {
                "line-width": [
                    "interpolate",
                    ["exponential", 1.5],
                    ["zoom"],
                    13,
                    [
                        "match",
                        ["get", "class"],
                        ["motorway", "trunk", "primary"],
                        6,
                        ["secondary", "tertiary"],
                        4,
                        [
                            "motorway_link",
                            "trunk_link",
                            "street",
                            "street_limited",
                            "primary_link"
                        ],
                        2.5,
                        1.25
                    ],
                    18,
                    [
                        "match",
                        ["get", "class"],
                        ["motorway", "trunk", "primary"],
                        36,
                        ["secondary", "tertiary"],
                        30,
                        [
                            "motorway_link",
                            "trunk_link",
                            "street",
                            "street_limited",
                            "primary_link"
                        ],
                        22,
                        16
                    ]
                ],
                "line-color": "hsl(40, 46%, 86%)"
            }
        },
        {
            "id": "bridge-simple",
            "type": "line",
            "metadata": {
                "mapbox:featureComponent": "road-network",
                "mapbox:group": "Road network, bridges"
            },
            "source": "mapbox-streets",
            "source-layer": "road",
            "minzoom": 13,
            "filter": [
                "all",
                ["==", ["get", "structure"], "bridge"],
                [
                    "step",
                    ["zoom"],
                    [
                        "match",
                        ["get", "class"],
                        ["motorway", "trunk"],
                        true,
                        false
                    ],
                    13,
                    [
                        "match",
                        ["get", "class"],
                        [
                            "motorway",
                            "motorway_link",
                            "trunk",
                            "trunk_link",
                            "primary",
                            "secondary",
                            "tertiary",
                            "street",
                            "street_limited",
                            "primary_link",
                            "track"
                        ],
                        true,
                        false
                    ],
                    14,
                    [
                        "match",
                        ["get", "class"],
                        [
                            "motorway",
                            "motorway_link",
                            "trunk",
                            "trunk_link",
                            "primary",
                            "primary_link",
                            "secondary",
                            "secondary_link",
                            "tertiary",
                            "tertiary_link",
                            "street",
                            "street_limited",
                            "service",
                            "track"
                        ],
                        true,
                        false
                    ]
                ],
                ["==", ["geometry-type"], "LineString"]
            ],
            "layout": {
                "line-cap": ["step", ["zoom"], "butt", 14, "round"],
                "line-join": ["step", ["zoom"], "miter", 14, "round"]
            },
            "paint": {
                "line-width": [
                    "interpolate",
                    ["exponential", 1.5],
                    ["zoom"],
                    13,
                    [
                        "match",
                        ["get", "class"],
                        ["motorway", "trunk", "primary"],
                        4,
                        ["secondary", "tertiary"],
                        2.5,
                        [
                            "motorway_link",
                            "trunk_link",
                            "street",
                            "street_limited",
                            "primary_link"
                        ],
                        1,
                        0.5
                    ],
                    18,
                    [
                        "match",
                        ["get", "class"],
                        ["motorway", "trunk", "primary"],
                        32,
                        ["secondary", "tertiary"],
                        26,
                        [
                            "motorway_link",
                            "trunk_link",
                            "street",
                            "street_limited",
                            "primary_link"
                        ],
                        18,
                        12
                    ]
                ],
                "line-color": [
                    "match",
                    ["get", "class"],
                    [
                        "primary_link",
                        "secondary_link",
                        "tertiary_link",
                        "street",
                        "street_limited",
                        "service",
                        "track"
                    ],
                    "hsl(38, 55%, 97%)",
                    "hsl(38, 55%, 100%)"
                ]
            }
        },
        {
            "id": "admin-1-boundary-bg",
            "type": "line",
            "metadata": {
                "mapbox:featureComponent": "admin-boundaries",
                "mapbox:group": "Administrative boundaries, admin"
            },
            "source": "mapbox-streets",
            "source-layer": "admin",
            "minzoom": 7,
            "filter": [
                "all",
                ["==", ["get", "admin_level"], 1],
                ["==", ["get", "maritime"], "false"],
                ["match", ["get", "worldview"], ["all", "US"], true, false]
            ],
            "layout": {"line-join": "bevel"},
            "paint": {
                "line-color": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    8,
                    "hsl(40, 46%, 86%)",
                    16,
                    "hsl(0, 0%, 87%)"
                ],
                "line-width": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    7,
                    3.75,
                    12,
                    5.5
                ],
                "line-opacity": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    7,
                    0,
                    8,
                    0.75
                ],
                "line-dasharray": [1, 0],
                "line-blur": ["interpolate", ["linear"], ["zoom"], 3, 0, 8, 3]
            }
        },
        {
            "id": "admin-0-boundary-bg",
            "type": "line",
            "metadata": {
                "mapbox:featureComponent": "admin-boundaries",
                "mapbox:group": "Administrative boundaries, admin"
            },
            "source": "mapbox-streets",
            "source-layer": "admin",
            "minzoom": 1,
            "filter": [
                "all",
                ["==", ["get", "admin_level"], 0],
                ["==", ["get", "maritime"], "false"],
                ["match", ["get", "worldview"], ["all", "US"], true, false]
            ],
            "layout": {},
            "paint": {
                "line-width": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    3,
                    3.5,
                    10,
                    8
                ],
                "line-color": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    6,
                    "hsl(40, 46%, 86%)",
                    8,
                    "hsl(0, 0%, 87%)"
                ],
                "line-opacity": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    3,
                    0,
                    4,
                    0.5
                ],
                "line-blur": ["interpolate", ["linear"], ["zoom"], 3, 0, 10, 2]
            }
        },
        {
            "id": "admin-1-boundary",
            "type": "line",
            "metadata": {
                "mapbox:featureComponent": "admin-boundaries",
                "mapbox:group": "Administrative boundaries, admin"
            },
            "source": "mapbox-streets",
            "source-layer": "admin",
            "minzoom": 2,
            "filter": [
                "all",
                ["==", ["get", "admin_level"], 1],
                ["==", ["get", "maritime"], "false"],
                ["match", ["get", "worldview"], ["all", "US"], true, false]
            ],
            "layout": {"line-join": "round", "line-cap": "round"},
            "paint": {
                "line-dasharray": [
                    "step",
                    ["zoom"],
                    ["literal", [2, 0]],
                    7,
                    ["literal", [2, 2, 6, 2]]
                ],
                "line-width": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    7,
                    0.75,
                    12,
                    1.5
                ],
                "line-opacity": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    2,
                    0,
                    3,
                    1
                ],
                "line-color": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    3,
                    "hsl(0, 0%, 77%)",
                    7,
                    "hsl(0, 0%, 62%)"
                ]
            }
        },
        {
            "id": "admin-0-boundary",
            "type": "line",
            "metadata": {
                "mapbox:featureComponent": "admin-boundaries",
                "mapbox:group": "Administrative boundaries, admin"
            },
            "source": "mapbox-streets",
            "source-layer": "admin",
            "minzoom": 1,
            "filter": [
                "all",
                ["==", ["get", "admin_level"], 0],
                ["==", ["get", "disputed"], "false"],
                ["==", ["get", "maritime"], "false"],
                ["match", ["get", "worldview"], ["all", "US"], true, false]
            ],
            "layout": {"line-join": "round", "line-cap": "round"},
            "paint": {
                "line-color": "hsl(0, 0%, 51%)",
                "line-width": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    3,
                    0.5,
                    10,
                    2
                ],
                "line-dasharray": [10, 0]
            }
        },
        {
            "id": "admin-0-boundary-disputed",
            "type": "line",
            "metadata": {
                "mapbox:featureComponent": "admin-boundaries",
                "mapbox:group": "Administrative boundaries, admin"
            },
            "source": "mapbox-streets",
            "source-layer": "admin",
            "minzoom": 1,
            "filter": [
                "all",
                ["==", ["get", "disputed"], "true"],
                ["==", ["get", "admin_level"], 0],
                ["==", ["get", "maritime"], "false"],
                ["match", ["get", "worldview"], ["all", "US"], true, false]
            ],
            "layout": {"line-join": "round"},
            "paint": {
                "line-color": "hsl(0, 0%, 51%)",
                "line-width": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    3,
                    0.5,
                    10,
                    2
                ],
                "line-dasharray": [
                    "step",
                    ["zoom"],
                    ["literal", [3.25, 3.25]],
                    6,
                    ["literal", [2.5, 2.5]],
                    7,
                    ["literal", [2, 2.25]],
                    8,
                    ["literal", [1.75, 2]]
                ]
            }
        },
        {
            "id": "road-label-simple",
            "type": "symbol",
            "metadata": {
                "mapbox:featureComponent": "road-network",
                "mapbox:group": "Road network, road-labels"
            },
            "source": "mapbox-streets",
            "source-layer": "road",
            "minzoom": 12,
            "filter": [
                "match",
                ["get", "class"],
                [
                    "motorway",
                    "trunk",
                    "primary",
                    "secondary",
                    "tertiary",
                    "street",
                    "street_limited"
                ],
                true,
                false
            ],
            "layout": {
                "text-size": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    10,
                    [
                        "match",
                        ["get", "class"],
                        [
                            "motorway",
                            "trunk",
                            "primary",
                            "secondary",
                            "tertiary"
                        ],
                        10,
                        9
                    ],
                    18,
                    [
                        "match",
                        ["get", "class"],
                        [
                            "motorway",
                            "trunk",
                            "primary",
                            "secondary",
                            "tertiary"
                        ],
                        16,
                        14
                    ]
                ],
                "text-max-angle": 30,
                "text-font": ["DIN Pro Regular", "Arial Unicode MS Regular"],
                "symbol-placement": "line",
                "text-padding": 1,
                "text-rotation-alignment": "map",
                "text-pitch-alignment": "viewport",
                "text-field": ["coalesce", ["get", "name_en"], ["get", "name"]],
                "text-letter-spacing": 0.01
            },
            "paint": {
                "text-color": "hsl(40, 47%, 41%)",
                "text-halo-color": "hsl(38, 55%, 100%)",
                "text-halo-width": 1
            }
        },
        {
            "id": "path-pedestrian-label",
            "type": "symbol",
            "metadata": {
                "mapbox:featureComponent": "walking-cycling",
                "mapbox:group": "Walking, cycling, etc., walking-cycling-labels"
            },
            "source": "mapbox-streets",
            "source-layer": "road",
            "minzoom": 12,
            "filter": [
                "step",
                ["zoom"],
                ["match", ["get", "class"], ["pedestrian"], true, false],
                15,
                ["match", ["get", "class"], ["path", "pedestrian"], true, false]
            ],
            "layout": {
                "text-size": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    10,
                    ["match", ["get", "class"], "pedestrian", 9, 6.5],
                    18,
                    ["match", ["get", "class"], "pedestrian", 14, 13]
                ],
                "text-max-angle": 30,
                "text-font": ["DIN Pro Regular", "Arial Unicode MS Regular"],
                "symbol-placement": "line",
                "text-padding": 1,
                "text-rotation-alignment": "map",
                "text-pitch-alignment": "viewport",
                "text-field": ["coalesce", ["get", "name_en"], ["get", "name"]],
                "text-letter-spacing": 0.01
            },
            "paint": {
                "text-color": "hsl(40, 47%, 41%)",
                "text-halo-color": "hsl(40, 46%, 95%)",
                "text-halo-width": 1,
                "text-halo-blur": 1
            }
        },
        {
            "id": "waterway-label",
            "type": "symbol",
            "metadata": {
                "mapbox:featureComponent": "natural-features",
                "mapbox:group": "Natural features, natural-labels"
            },
            "source": "mapbox-streets",
            "source-layer": "natural_label",
            "minzoom": 13,
            "filter": [
                "all",
                [
                    "match",
                    ["get", "class"],
                    ["canal", "river", "stream"],
                    ["match", ["get", "worldview"], ["all", "US"], true, false],
                    ["disputed_canal", "disputed_river", "disputed_stream"],
                    [
                        "all",
                        ["==", ["get", "disputed"], "true"],
                        [
                            "match",
                            ["get", "worldview"],
                            ["all", "US"],
                            true,
                            false
                        ]
                    ],
                    false
                ],
                ["==", ["geometry-type"], "LineString"]
            ],
            "layout": {
                "text-font": ["DIN Pro Italic", "Arial Unicode MS Regular"],
                "text-max-angle": 30,
                "symbol-spacing": [
                    "interpolate",
                    ["linear", 1],
                    ["zoom"],
                    15,
                    250,
                    17,
                    400
                ],
                "text-size": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    13,
                    12,
                    18,
                    16
                ],
                "symbol-placement": "line",
                "text-pitch-alignment": "viewport",
                "text-field": ["coalesce", ["get", "name_en"], ["get", "name"]]
            },
            "paint": {"text-color": "hsl(205, 44%, 90%)"}
        },
        {
            "id": "natural-line-label",
            "type": "symbol",
            "metadata": {
                "mapbox:featureComponent": "natural-features",
                "mapbox:group": "Natural features, natural-labels"
            },
            "source": "mapbox-streets",
            "source-layer": "natural_label",
            "minzoom": 4,
            "filter": [
                "all",
                [
                    "match",
                    ["get", "class"],
                    ["glacier", "landform"],
                    ["match", ["get", "worldview"], ["all", "US"], true, false],
                    ["disputed_glacier", "disputed_landform"],
                    [
                        "all",
                        ["==", ["get", "disputed"], "true"],
                        [
                            "match",
                            ["get", "worldview"],
                            ["all", "US"],
                            true,
                            false
                        ]
                    ],
                    false
                ],
                ["==", ["geometry-type"], "LineString"],
                ["<=", ["get", "filterrank"], 2]
            ],
            "layout": {
                "text-size": [
                    "step",
                    ["zoom"],
                    ["step", ["get", "sizerank"], 18, 5, 12],
                    17,
                    ["step", ["get", "sizerank"], 18, 13, 12]
                ],
                "text-max-angle": 30,
                "text-field": ["coalesce", ["get", "name_en"], ["get", "name"]],
                "text-font": ["DIN Pro Medium", "Arial Unicode MS Regular"],
                "symbol-placement": "line-center",
                "text-pitch-alignment": "viewport"
            },
            "paint": {
                "text-halo-width": 0.5,
                "text-halo-color": "hsl(40, 53%, 100%)",
                "text-halo-blur": 0.5,
                "text-color": [
                    "step",
                    ["zoom"],
                    [
                        "step",
                        ["get", "sizerank"],
                        "hsl(26, 30%, 45%)",
                        5,
                        "hsl(26, 35%, 35%)"
                    ],
                    17,
                    [
                        "step",
                        ["get", "sizerank"],
                        "hsl(26, 30%, 45%)",
                        13,
                        "hsl(26, 35%, 35%)"
                    ]
                ]
            }
        },
        {
            "id": "natural-point-label",
            "type": "symbol",
            "metadata": {
                "mapbox:featureComponent": "natural-features",
                "mapbox:group": "Natural features, natural-labels"
            },
            "source": "mapbox-streets",
            "source-layer": "natural_label",
            "minzoom": 4,
            "filter": [
                "all",
                [
                    "match",
                    ["get", "class"],
                    ["dock", "glacier", "landform", "water_feature", "wetland"],
                    ["match", ["get", "worldview"], ["all", "US"], true, false],
                    [
                        "disputed_dock",
                        "disputed_glacier",
                        "disputed_landform",
                        "disputed_water_feature",
                        "disputed_wetland"
                    ],
                    [
                        "all",
                        ["==", ["get", "disputed"], "true"],
                        [
                            "match",
                            ["get", "worldview"],
                            ["all", "US"],
                            true,
                            false
                        ]
                    ],
                    false
                ],
                ["==", ["geometry-type"], "Point"],
                ["<=", ["get", "filterrank"], 2]
            ],
            "layout": {
                "text-size": [
                    "step",
                    ["zoom"],
                    ["step", ["get", "sizerank"], 18, 5, 12],
                    17,
                    ["step", ["get", "sizerank"], 18, 13, 12]
                ],
                "icon-image": ["get", "maki"],
                "text-font": ["DIN Pro Medium", "Arial Unicode MS Regular"],
                "text-offset": [
                    "step",
                    ["zoom"],
                    [
                        "step",
                        ["get", "sizerank"],
                        ["literal", [0, 0]],
                        5,
                        ["literal", [0, 0.75]]
                    ],
                    17,
                    [
                        "step",
                        ["get", "sizerank"],
                        ["literal", [0, 0]],
                        13,
                        ["literal", [0, 0.75]]
                    ]
                ],
                "text-anchor": [
                    "step",
                    ["zoom"],
                    ["step", ["get", "sizerank"], "center", 5, "top"],
                    17,
                    ["step", ["get", "sizerank"], "center", 13, "top"]
                ],
                "text-field": ["coalesce", ["get", "name_en"], ["get", "name"]]
            },
            "paint": {
                "icon-opacity": [
                    "step",
                    ["zoom"],
                    ["step", ["get", "sizerank"], 0, 5, 1],
                    17,
                    ["step", ["get", "sizerank"], 0, 13, 1]
                ],
                "text-halo-color": "hsl(40, 53%, 100%)",
                "text-halo-width": 0.5,
                "text-halo-blur": 0.5,
                "text-color": [
                    "step",
                    ["zoom"],
                    [
                        "step",
                        ["get", "sizerank"],
                        "hsl(26, 30%, 45%)",
                        5,
                        "hsl(26, 35%, 35%)"
                    ],
                    17,
                    [
                        "step",
                        ["get", "sizerank"],
                        "hsl(26, 30%, 45%)",
                        13,
                        "hsl(26, 35%, 35%)"
                    ]
                ]
            }
        },
        {
            "id": "water-line-label",
            "type": "symbol",
            "metadata": {
                "mapbox:featureComponent": "natural-features",
                "mapbox:group": "Natural features, natural-labels"
            },
            "source": "mapbox-streets",
            "source-layer": "natural_label",
            "filter": [
                "all",
                [
                    "match",
                    ["get", "class"],
                    ["bay", "ocean", "reservoir", "sea", "water"],
                    ["match", ["get", "worldview"], ["all", "US"], true, false],
                    [
                        "disputed_bay",
                        "disputed_ocean",
                        "disputed_reservoir",
                        "disputed_sea",
                        "disputed_water"
                    ],
                    [
                        "all",
                        ["==", ["get", "disputed"], "true"],
                        [
                            "match",
                            ["get", "worldview"],
                            ["all", "US"],
                            true,
                            false
                        ]
                    ],
                    false
                ],
                ["==", ["geometry-type"], "LineString"]
            ],
            "layout": {
                "text-size": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    7,
                    ["step", ["get", "sizerank"], 20, 6, 18, 12, 12],
                    10,
                    ["step", ["get", "sizerank"], 15, 9, 12],
                    18,
                    ["step", ["get", "sizerank"], 15, 9, 14]
                ],
                "text-max-angle": 30,
                "text-letter-spacing": [
                    "match",
                    ["get", "class"],
                    "ocean",
                    0.25,
                    ["sea", "bay"],
                    0.15,
                    0
                ],
                "text-font": ["DIN Pro Italic", "Arial Unicode MS Regular"],
                "symbol-placement": "line-center",
                "text-pitch-alignment": "viewport",
                "text-field": ["coalesce", ["get", "name_en"], ["get", "name"]]
            },
            "paint": {
                "text-color": [
                    "match",
                    ["get", "class"],
                    ["bay", "ocean", "sea"],
                    "hsl(205, 72%, 90%)",
                    "hsl(205, 44%, 90%)"
                ]
            }
        },
        {
            "id": "water-point-label",
            "type": "symbol",
            "metadata": {
                "mapbox:featureComponent": "natural-features",
                "mapbox:group": "Natural features, natural-labels"
            },
            "source": "mapbox-streets",
            "source-layer": "natural_label",
            "filter": [
                "all",
                [
                    "match",
                    ["get", "class"],
                    ["bay", "ocean", "reservoir", "sea", "water"],
                    ["match", ["get", "worldview"], ["all", "US"], true, false],
                    [
                        "disputed_bay",
                        "disputed_ocean",
                        "disputed_reservoir",
                        "disputed_sea",
                        "disputed_water"
                    ],
                    [
                        "all",
                        ["==", ["get", "disputed"], "true"],
                        [
                            "match",
                            ["get", "worldview"],
                            ["all", "US"],
                            true,
                            false
                        ]
                    ],
                    false
                ],
                ["==", ["geometry-type"], "Point"]
            ],
            "layout": {
                "text-line-height": 1.3,
                "text-size": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    7,
                    ["step", ["get", "sizerank"], 20, 6, 15, 12, 12],
                    10,
                    ["step", ["get", "sizerank"], 15, 9, 12]
                ],
                "text-font": ["DIN Pro Italic", "Arial Unicode MS Regular"],
                "text-field": ["coalesce", ["get", "name_en"], ["get", "name"]],
                "text-letter-spacing": [
                    "match",
                    ["get", "class"],
                    "ocean",
                    0.25,
                    ["bay", "sea"],
                    0.15,
                    0.01
                ],
                "text-max-width": [
                    "match",
                    ["get", "class"],
                    "ocean",
                    4,
                    "sea",
                    5,
                    ["bay", "water"],
                    7,
                    10
                ]
            },
            "paint": {
                "text-color": [
                    "match",
                    ["get", "class"],
                    ["bay", "ocean", "sea"],
                    "hsl(205, 72%, 90%)",
                    "hsl(205, 44%, 90%)"
                ]
            }
        },
        {
            "id": "poi-label",
            "type": "symbol",
            "metadata": {
                "mapbox:featureComponent": "point-of-interest-labels",
                "mapbox:group": "Point of interest labels, poi-labels"
            },
            "source": "mapbox-streets",
            "source-layer": "poi_label",
            "minzoom": 6,
            "filter": [
                "<=",
                ["get", "filterrank"],
                ["+", ["step", ["zoom"], 0, 16, 1, 17, 2], 2]
            ],
            "layout": {
                "text-size": [
                    "step",
                    ["zoom"],
                    ["step", ["get", "sizerank"], 18, 5, 12],
                    17,
                    ["step", ["get", "sizerank"], 18, 13, 12]
                ],
                "icon-image": [
                    "case",
                    ["has", "maki_beta"],
                    [
                        "coalesce",
                        ["image", ["get", "maki_beta"]],
                        ["image", ["get", "maki"]]
                    ],
                    ["image", ["get", "maki"]]
                ],
                "text-font": ["DIN Pro Medium", "Arial Unicode MS Regular"],
                "text-offset": [
                    "step",
                    ["zoom"],
                    [
                        "step",
                        ["get", "sizerank"],
                        ["literal", [0, 0]],
                        5,
                        ["literal", [0, 0.75]]
                    ],
                    17,
                    [
                        "step",
                        ["get", "sizerank"],
                        ["literal", [0, 0]],
                        13,
                        ["literal", [0, 0.75]]
                    ]
                ],
                "text-anchor": [
                    "step",
                    ["zoom"],
                    ["step", ["get", "sizerank"], "center", 5, "top"],
                    17,
                    ["step", ["get", "sizerank"], "center", 13, "top"]
                ],
                "text-field": ["coalesce", ["get", "name_en"], ["get", "name"]]
            },
            "paint": {
                "icon-opacity": [
                    "step",
                    ["zoom"],
                    ["step", ["get", "sizerank"], 0, 5, 1],
                    17,
                    ["step", ["get", "sizerank"], 0, 13, 1]
                ],
                "text-halo-color": [
                    "match",
                    ["get", "class"],
                    "park_like",
                    "hsl(78, 55%, 100%)",
                    "education",
                    "hsl(40, 52%, 100%)",
                    "medical",
                    "hsl(3, 51%, 100%)",
                    "hsl(40, 53%, 100%)"
                ],
                "text-halo-width": 0.5,
                "text-halo-blur": 0.5,
                "text-color": [
                    "step",
                    ["zoom"],
                    [
                        "step",
                        ["get", "sizerank"],
                        [
                            "match",
                            ["get", "class"],
                            "food_and_drink",
                            "hsl(20, 42%, 58%)",
                            "park_like",
                            "hsl(76, 51%, 26%)",
                            "education",
                            "hsl(40, 18%, 45%)",
                            "medical",
                            "hsl(3, 18%, 55%)",
                            "hsl(26, 30%, 45%)"
                        ],
                        5,
                        [
                            "match",
                            ["get", "class"],
                            "food_and_drink",
                            "hsl(20, 74%, 41%)",
                            "park_like",
                            "hsl(76, 50%, 15%)",
                            "education",
                            "hsl(40, 45%, 25%)",
                            "medical",
                            "hsl(3, 24%, 45%)",
                            "hsl(26, 35%, 35%)"
                        ]
                    ],
                    17,
                    [
                        "step",
                        ["get", "sizerank"],
                        [
                            "match",
                            ["get", "class"],
                            "food_and_drink",
                            "hsl(20, 42%, 58%)",
                            "park_like",
                            "hsl(76, 51%, 26%)",
                            "education",
                            "hsl(40, 18%, 45%)",
                            "medical",
                            "hsl(3, 18%, 55%)",
                            "hsl(26, 30%, 45%)"
                        ],
                        13,
                        [
                            "match",
                            ["get", "class"],
                            "food_and_drink",
                            "hsl(20, 74%, 41%)",
                            "park_like",
                            "hsl(76, 50%, 15%)",
                            "education",
                            "hsl(40, 45%, 25%)",
                            "medical",
                            "hsl(3, 24%, 45%)",
                            "hsl(26, 35%, 35%)"
                        ]
                    ]
                ]
            }
        },
        {
            "id": "airport-label",
            "type": "symbol",
            "metadata": {
                "mapbox:featureComponent": "transit",
                "mapbox:group": "Transit, transit-labels"
            },
            "source": "mapbox-streets",
            "source-layer": "airport_label",
            "minzoom": 8,
            "filter": [
                "match",
                ["get", "class"],
                ["military", "civil"],
                ["match", ["get", "worldview"], ["all", "US"], true, false],
                ["disputed_military", "disputed_civil"],
                [
                    "all",
                    ["==", ["get", "disputed"], "true"],
                    ["match", ["get", "worldview"], ["all", "US"], true, false]
                ],
                false
            ],
            "layout": {
                "text-line-height": 1.1,
                "text-size": ["step", ["get", "sizerank"], 18, 9, 12],
                "icon-image": ["get", "maki"],
                "text-font": ["DIN Pro Medium", "Arial Unicode MS Regular"],
                "text-offset": [0, 0.75],
                "text-rotation-alignment": "viewport",
                "text-anchor": "top",
                "text-field": [
                    "step",
                    ["get", "sizerank"],
                    ["coalesce", ["get", "name_en"], ["get", "name"]],
                    15,
                    ["get", "ref"]
                ],
                "text-letter-spacing": 0.01,
                "text-max-width": 9
            },
            "paint": {
                "text-color": "hsl(225, 4%, 40%)",
                "text-halo-color": "hsl(225, 68%, 100%)",
                "text-halo-width": 1
            }
        },
        {
            "id": "settlement-subdivision-label",
            "type": "symbol",
            "metadata": {
                "mapbox:featureComponent": "place-labels",
                "mapbox:group": "Place labels, place-labels"
            },
            "source": "mapbox-streets",
            "source-layer": "place_label",
            "minzoom": 10,
            "maxzoom": 15,
            "filter": [
                "all",
                [
                    "match",
                    ["get", "class"],
                    "settlement_subdivision",
                    ["match", ["get", "worldview"], ["all", "US"], true, false],
                    "disputed_settlement_subdivision",
                    [
                        "all",
                        ["==", ["get", "disputed"], "true"],
                        [
                            "match",
                            ["get", "worldview"],
                            ["all", "US"],
                            true,
                            false
                        ]
                    ],
                    false
                ],
                ["<=", ["get", "filterrank"], 3]
            ],
            "layout": {
                "text-field": ["coalesce", ["get", "name_en"], ["get", "name"]],
                "text-transform": "uppercase",
                "text-font": ["DIN Pro Regular", "Arial Unicode MS Regular"],
                "text-letter-spacing": [
                    "match",
                    ["get", "type"],
                    "suburb",
                    0.15,
                    0.1
                ],
                "text-max-width": 7,
                "text-padding": 3,
                "text-size": [
                    "interpolate",
                    ["cubic-bezier", 0.5, 0, 1, 1],
                    ["zoom"],
                    11,
                    ["match", ["get", "type"], "suburb", 11, 10.5],
                    15,
                    ["match", ["get", "type"], "suburb", 15, 14]
                ]
            },
            "paint": {
                "text-halo-color": "hsla(40, 53%, 100%, 0.75)",
                "text-halo-width": 1,
                "text-color": "hsl(0, 0%, 27%)",
                "text-halo-blur": 0.5
            }
        },
        {
            "id": "settlement-minor-label",
            "type": "symbol",
            "metadata": {
                "mapbox:featureComponent": "place-labels",
                "mapbox:group": "Place labels, place-labels"
            },
            "source": "mapbox-streets",
            "source-layer": "place_label",
            "minzoom": 3,
            "maxzoom": 13,
            "filter": [
                "all",
                ["<=", ["get", "filterrank"], 3],
                [
                    "match",
                    ["get", "class"],
                    "settlement",
                    ["match", ["get", "worldview"], ["all", "US"], true, false],
                    "disputed_settlement",
                    [
                        "all",
                        ["==", ["get", "disputed"], "true"],
                        [
                            "match",
                            ["get", "worldview"],
                            ["all", "US"],
                            true,
                            false
                        ]
                    ],
                    false
                ],
                [
                    "step",
                    ["zoom"],
                    [">", ["get", "symbolrank"], 6],
                    4,
                    [">=", ["get", "symbolrank"], 7],
                    6,
                    [">=", ["get", "symbolrank"], 8],
                    7,
                    [">=", ["get", "symbolrank"], 10],
                    10,
                    [">=", ["get", "symbolrank"], 11],
                    11,
                    [">=", ["get", "symbolrank"], 13],
                    12,
                    [">=", ["get", "symbolrank"], 15]
                ]
            ],
            "layout": {
                "icon-image": "",
                "text-font": ["DIN Pro Regular", "Arial Unicode MS Regular"],
                "text-radial-offset": [
                    "step",
                    ["zoom"],
                    ["match", ["get", "capital"], 2, 0.6, 0.55],
                    8,
                    0
                ],
                "text-anchor": ["step", ["zoom"], "center", 8, "center"],
                "text-field": ["coalesce", ["get", "name_en"], ["get", "name"]],
                "text-max-width": 7,
                "text-line-height": 1.1,
                "text-size": [
                    "interpolate",
                    ["cubic-bezier", 0.2, 0, 0.9, 1],
                    ["zoom"],
                    3,
                    [
                        "step",
                        ["get", "symbolrank"],
                        12,
                        9,
                        11,
                        10,
                        10.5,
                        12,
                        9.5,
                        14,
                        8.5,
                        16,
                        6.5,
                        17,
                        4
                    ],
                    13,
                    [
                        "step",
                        ["get", "symbolrank"],
                        23,
                        9,
                        21,
                        10,
                        19,
                        11,
                        17,
                        12,
                        16,
                        13,
                        15,
                        15,
                        13
                    ]
                ]
            },
            "paint": {
                "text-color": "hsl(0, 0%, 0%)",
                "text-halo-color": "hsl(40, 53%, 100%)",
                "text-halo-width": 1,
                "icon-opacity": ["step", ["zoom"], 1, 8, 0],
                "text-halo-blur": 1
            }
        },
        {
            "id": "settlement-major-label",
            "type": "symbol",
            "metadata": {
                "mapbox:featureComponent": "place-labels",
                "mapbox:group": "Place labels, place-labels"
            },
            "source": "mapbox-streets",
            "source-layer": "place_label",
            "minzoom": 3,
            "maxzoom": 15,
            "filter": [
                "all",
                ["<=", ["get", "filterrank"], 3],
                [
                    "match",
                    ["get", "class"],
                    "settlement",
                    ["match", ["get", "worldview"], ["all", "US"], true, false],
                    "disputed_settlement",
                    [
                        "all",
                        ["==", ["get", "disputed"], "true"],
                        [
                            "match",
                            ["get", "worldview"],
                            ["all", "US"],
                            true,
                            false
                        ]
                    ],
                    false
                ],
                [
                    "step",
                    ["zoom"],
                    false,
                    3,
                    ["<=", ["get", "symbolrank"], 6],
                    4,
                    ["<", ["get", "symbolrank"], 7],
                    6,
                    ["<", ["get", "symbolrank"], 8],
                    7,
                    ["<", ["get", "symbolrank"], 10],
                    10,
                    ["<", ["get", "symbolrank"], 11],
                    11,
                    ["<", ["get", "symbolrank"], 13],
                    12,
                    ["<", ["get", "symbolrank"], 15],
                    13,
                    [">=", ["get", "symbolrank"], 11],
                    14,
                    [">=", ["get", "symbolrank"], 15]
                ]
            ],
            "layout": {
                "icon-image": "",
                "text-font": ["DIN Pro Medium", "Arial Unicode MS Regular"],
                "text-radial-offset": [
                    "step",
                    ["zoom"],
                    ["match", ["get", "capital"], 2, 0.6, 0.55],
                    8,
                    0
                ],
                "text-anchor": ["step", ["zoom"], "center", 8, "center"],
                "text-field": ["coalesce", ["get", "name_en"], ["get", "name"]],
                "text-max-width": 7,
                "text-line-height": 1.1,
                "text-size": [
                    "interpolate",
                    ["cubic-bezier", 0.2, 0, 0.9, 1],
                    ["zoom"],
                    3,
                    ["step", ["get", "symbolrank"], 13, 6, 12],
                    6,
                    ["step", ["get", "symbolrank"], 16, 6, 15, 7, 14],
                    8,
                    ["step", ["get", "symbolrank"], 18, 9, 17, 10, 15],
                    15,
                    [
                        "step",
                        ["get", "symbolrank"],
                        23,
                        9,
                        22,
                        10,
                        20,
                        11,
                        18,
                        12,
                        16,
                        13,
                        15,
                        15,
                        13
                    ]
                ]
            },
            "paint": {
                "text-color": "hsl(0, 0%, 0%)",
                "text-halo-color": "hsl(40, 53%, 100%)",
                "text-halo-width": 1,
                "icon-opacity": ["step", ["zoom"], 1, 8, 0],
                "text-halo-blur": 1
            }
        },
        {
            "id": "state-label",
            "type": "symbol",
            "metadata": {
                "mapbox:featureComponent": "place-labels",
                "mapbox:group": "Place labels, place-labels"
            },
            "source": "mapbox-streets",
            "source-layer": "place_label",
            "minzoom": 3,
            "maxzoom": 9,
            "filter": [
                "match",
                ["get", "class"],
                "state",
                ["match", ["get", "worldview"], ["all", "US"], true, false],
                "disputed_state",
                [
                    "all",
                    ["==", ["get", "disputed"], "true"],
                    ["match", ["get", "worldview"], ["all", "US"], true, false]
                ],
                false
            ],
            "layout": {
                "text-size": [
                    "interpolate",
                    ["cubic-bezier", 0.85, 0.7, 0.65, 1],
                    ["zoom"],
                    4,
                    ["step", ["get", "symbolrank"], 10, 6, 9.5, 7, 9],
                    9,
                    ["step", ["get", "symbolrank"], 21, 6, 16, 7, 13]
                ],
                "text-transform": "uppercase",
                "text-font": ["DIN Pro Bold", "Arial Unicode MS Bold"],
                "text-field": [
                    "step",
                    ["zoom"],
                    [
                        "step",
                        ["get", "symbolrank"],
                        ["coalesce", ["get", "name_en"], ["get", "name"]],
                        5,
                        [
                            "coalesce",
                            ["get", "abbr"],
                            ["get", "name_en"],
                            ["get", "name"]
                        ]
                    ],
                    5,
                    ["coalesce", ["get", "name_en"], ["get", "name"]]
                ],
                "text-letter-spacing": 0.15,
                "text-max-width": 6
            },
            "paint": {
                "text-color": "hsl(0, 0%, 0%)",
                "text-halo-color": "hsl(40, 53%, 100%)",
                "text-halo-width": 1
            }
        },
        {
            "id": "country-label",
            "type": "symbol",
            "metadata": {
                "mapbox:featureComponent": "place-labels",
                "mapbox:group": "Place labels, place-labels"
            },
            "source": "mapbox-streets",
            "source-layer": "place_label",
            "minzoom": 1,
            "maxzoom": 10,
            "filter": [
                "match",
                ["get", "class"],
                "country",
                ["match", ["get", "worldview"], ["all", "US"], true, false],
                "disputed_country",
                [
                    "all",
                    ["==", ["get", "disputed"], "true"],
                    ["match", ["get", "worldview"], ["all", "US"], true, false]
                ],
                false
            ],
            "layout": {
                "icon-image": "",
                "text-field": ["coalesce", ["get", "name_en"], ["get", "name"]],
                "text-line-height": 1.1,
                "text-max-width": 6,
                "text-font": ["DIN Pro Medium", "Arial Unicode MS Regular"],
                "text-radial-offset": ["step", ["zoom"], 0.6, 8, 0],
                "text-size": [
                    "interpolate",
                    ["cubic-bezier", 0.2, 0, 0.7, 1],
                    ["zoom"],
                    1,
                    ["step", ["get", "symbolrank"], 11, 4, 9, 5, 8],
                    9,
                    ["step", ["get", "symbolrank"], 22, 4, 19, 5, 17]
                ]
            },
            "paint": {
                "icon-opacity": [
                    "step",
                    ["zoom"],
                    ["case", ["has", "text_anchor"], 1, 0],
                    7,
                    0
                ],
                "text-color": "hsl(0, 0%, 0%)",
                "text-halo-color": [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    2,
                    "hsla(40, 53%, 100%, 0.75)",
                    3,
                    "hsl(40, 53%, 100%)"
                ],
                "text-halo-width": 1.25
            }
        }
    ]', FALSE, '', TRUE, TRUE);

INSERT INTO map_layers(maplayerid, name, layerdefinitions, isoverlay, icon, activated, addtomap)
   VALUES (public.uuid_generate_v1mc(), 'mapzen', '
     [
     {
         "id": "background",
         "type": "background",
         "paint": {
           "background-color": "#ededed"
         }
       }, {
         "id": "water-line",
         "source": "mapzen",
         "source-layer": "water",
         "type": "line",
         "filter": ["==", "$type", "LineString"],
         "paint": {
           "line-color": "#7acad0",
           "line-width": {
             "base": 1.2,
             "stops": [[8, 0.5], [20, 15]]
           }
         }
       }, {
         "id": "water-polygon",
         "source": "mapzen",
         "source-layer": "water",
         "type": "fill",
         "filter": ["==", "$type", "Polygon"],
         "paint": {
           "fill-color": "#7acad0"
         }
       }, {
         "id": "park",
         "type": "fill",
         "source": "mapzen",
         "source-layer": "landuse",
         "minzoom": 6,
         "filter": ["in", "kind", "park", "forest", "garden", "grass", "farm", "meadow", "playground", "golf_course", "nature_reserve", "wetland", "wood", "cemetery"],
         "paint": {
           "fill-color": "#c2cd44"
         }
       }, {
         "id": "river",
         "source": "mapzen",
         "source-layer": "water",
         "type": "line",
         "minzoom": 6,
         "filter": ["all", ["==", "$type", "LineString"], ["==", "kind", "river"]],
         "layout": {
             "line-cap": "round",
             "line-join": "round"
           },
         "paint": {
           "line-color": "#7acad0",
           "line-width": {
             "base": 1.2,
             "stops": [[8, 0.75], [20, 15]]
           }
         }
       }, {
         "id": "stream-etc",
         "source": "mapzen",
         "source-layer": "water",
         "type": "line",
         "minzoom": 11,
         "filter": ["all", ["==", "$type", "LineString"], ["==", "kind", "stream"]],
         "layout": {
             "line-cap": "round",
             "line-join": "round"
           },
         "paint": {
           "line-color": "#7acad0",
           "line-width": {
             "base": 1.4,
             "stops": [[10, 0.5], [20, 15]]
           }
         }
       }, {
           "id": "country-boundary",
           "source": "mapzen",
           "source-layer": "places",
           "type": "line",
           "filter": ["==", "admin_level", "2"],
           "maxzoom": 4,
           "layout": {
             "line-cap": "round",
             "line-join": "round"
           },
           "paint": {
             "line-color": "#afd3d3",
           "line-width": {
             "base": 2,
             "stops": [[1, 0.5], [7, 3]]
             }
           }
         }, {
           "id": "state-boundary",
           "source": "mapzen",
           "source-layer": "places",
           "type": "fill",
           "filter": ["==", "admin_level", "4"],
           "maxzoom": 10,
           "paint": {
             "fill-color": "#ededed",
             "fill-outline-color": "#cacecc"
           }
         }, {
         "id": "subways",
         "source": "mapzen",
         "source-layer": "roads",
         "type": "line",
         "paint": {
           "line-color": "#ef7369",
           "line-dasharray": [2, 1]
         },
         "filter": ["==", "railway", "subway"]
       }, {
         "id": "link-tunnel",
         "source": "mapzen",
         "source-layer": "roads",
         "type": "line",
         "filter": ["any",["==", "is_tunnel", "yes"]],
         "layout": {
           "line-join": "round",
           "line-cap": "round"
         },
         "paint": {
           "line-color": "#afd3d3",
           "line-width": {
             "base": 1.55,
             "stops": [[4, 0.25], [20, 30]]
           },
           "line-dasharray": [1, 2]
         }
       }, {
         "id": "buildings",
         "type": "fill",
         "source": "mapzen",
         "source-layer": "buildings",
         "paint": {
         "fill-outline-color": "#afd3d3",
         "fill-color": "#ededed"
         }
       }, {
         "id": "road",
         "source": "mapzen",
         "source-layer": "roads",
         "type": "line",
         "filter": ["any",["==", "kind", "minor_road"],["==", "kind", "major_road"]],
         "layout": {
           "line-join": "round",
           "line-cap": "round"
         },
         "paint": {
           "line-color": "#c0c4c2",
           "line-width": {
             "base": 1.55,
             "stops": [[4, 0.25], [20, 30]]
           }
         }
       }, {
         "id": "link-bridge",
         "source": "mapzen",
         "source-layer": "roads",
         "type": "line",
         "filter": ["any",["==", "is_link", "yes"], ["==", "is_bridge", "yes"]],
         "layout": {
           "line-join": "round",
           "line-cap": "round"
         },
         "paint": {
           "line-color": "#c0c4c2",
           "line-width": {
             "base": 1.55,
             "stops": [[4, 0.5], [8, 1.5], [20, 40]]
           }
         }
       }, {
         "id": "highway",
         "source": "mapzen",
         "source-layer": "roads",
         "type": "line",
         "filter": ["==", "kind", "highway"],
         "layout": {
           "line-join": "round",
           "line-cap": "round"
         },
         "paint": {
           "line-color": "#5d6765",
           "line-width": {
             "base": 1.55,
             "stops": [[4, 0.5], [8, 1.5], [20, 40]]
           }
         }
       }, {
         "id": "path",
         "source": "mapzen",
         "source-layer": "roads",
         "type": "line",
         "filter": ["==", "kind", "path"],
         "layout": {
           "line-join": "round",
           "line-cap": "round"
         },
         "minzoom": 12,
         "paint": {
           "line-color": "#5d6765",
           "line-width": {
             "base": 1.8,
             "stops": [[10, 0.15], [20, 15]]
           },
           "line-dasharray": [2, 2]
         }
       }, {
         "id": "ocean-label",
         "source": "mapzen",
         "source-layer": "places",
         "type": "symbol",
         "minzoom": 2,
         "maxzoom": 6,
         "filter": ["==", "kind", "ocean"],
         "layout": {
             "text-field": "{name}",
             "text-font": ["Open Sans Italic", "Arial Unicode MS Regular"],
             "text-max-width": 14,
             "text-letter-spacing": 0.1
           },
         "paint": {
           "text-color": "#ededed",
           "text-halo-color": "rgba(0,0,0,0.2)"
         }
       }, {
           "id": "other-label",
           "source": "mapzen",
           "source-layer": "places",
           "filter": ["all", ["==", "$type", "Point"], ["==", "kind", "neighbourhood"]],
           "minzoom": 12,
           "type": "symbol",
           "layout": {
             "text-field": "{name}",
             "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
             "text-max-width": 10
           },
           "paint": {
             "text-color": "#cb4b49",
             "text-halo-color": "rgba(255,255,255,0.5)"
           }
         }, {
           "id": "city-label",
           "source": "mapzen",
           "source-layer": "places",
           "filter": ["all", ["==", "$type", "Point"], ["==", "kind", "city"]],
           "minzoom": 10,
           "maxzoom": 14,
           "type": "symbol",
           "layout": {
             "text-field": "{name}",
             "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
             "text-max-width": 10,
             "text-letter-spacing": 0.1
           },
           "paint": {
             "text-color": "#384646",
             "text-halo-color": "rgba(255,255,255,0.5)"
           }
         }, {
           "id": "state-label",
           "source": "mapzen",
           "source-layer": "places",
           "filter": ["all", ["==", "$type", "Point"], ["==", "kind", "state"]],
           "minzoom": 6,
           "maxzoom": 12,
           "type": "symbol",
           "layout": {
             "text-field": "{name}",
             "text-font": ["Open Sans Regular", "Arial Unicode MS Regular"],
             "text-max-width": 8
           },
           "paint": {
             "text-color": "#f27a87",
             "text-halo-color": "rgba(255,255,255,0.5)"
           }
         }, {
           "id": "country-label",
           "source": "mapzen",
           "source-layer": "places",
           "filter": ["all", ["==", "$type", "Point"], ["==", "kind", "country"]],
           "maxzoom": 7,
           "type": "symbol",
           "layout": {
             "text-field": "{name}",
             "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
             "text-max-width": 4
           },
           "paint": {
             "text-color": "#cb4b49",
             "text-halo-color": "rgba(255,255,255,0.5)"
           }
         }
       ]', FALSE, '', TRUE, FALSE);

INSERT INTO report_templates(templateid, name, description, component, componentname, defaultconfig)
    VALUES ('50000000-0000-0000-0000-000000000001', 'No Header Template', 'Default Template', 'reports/default', 'default-report', '{}');

INSERT INTO report_templates(templateid, name, description, component, componentname, defaultconfig)
    VALUES ('50000000-0000-0000-0000-000000000002', 'Map Header Template', 'Map Widget', 'reports/map', 'map-report', '{
        "basemap": "streets",
        "geometryTypes": [{"text":"Point", "id":"Point"}, {"text":"Line", "id":"Line"}, {"text":"Polygon", "id":"Polygon"}],
        "overlayConfigs": [],
        "overlayOpacity": 0.0,
        "geocodeProvider": "MapzenGeocoder",
        "zoom": 10,
        "maxZoom": 20,
        "minZoom": 0,
        "centerX": -122.3979693,
        "centerY": 37.79,
        "pitch": 0.0,
        "bearing": 0.0,
        "geocodePlaceholder": "Search",
        "geocoderVisible": true,
        "featureColor": null,
        "featureLineWidth": null,
        "featurePointSize": null,
        "featureEditingDisabled": true,
        "mapControlsHidden": false
    }');

INSERT INTO report_templates(templateid, name, description, component, componentname, defaultconfig)
    VALUES ('50000000-0000-0000-0000-000000000003', 'Image Header Template', 'Image Header', 'reports/image', 'image-report', '{"nodes": []}');

CREATE MATERIALIZED VIEW mv_geojson_geoms AS
    SELECT t.tileid,
       t.resourceinstanceid,
       n.nodeid,
       st_transform(
           ST_SetSRID(
               st_geomfromgeojson((json_array_elements(t.tiledata::json -> n.nodeid::text -> 'features') -> 'geometry')::text),
               4326
           ), 900913)::geometry(Geometry,900913) AS geom
      FROM tiles t
    	LEFT JOIN nodes n ON t.nodegroupid = n.nodegroupid
     WHERE (( SELECT count(*) AS count
    		  FROM jsonb_object_keys(t.tiledata) jsonb_object_keys(jsonb_object_keys)
    		 WHERE (jsonb_object_keys.jsonb_object_keys IN ( SELECT n_1.nodeid::text AS nodeid
    				  FROM nodes n_1
    				 WHERE n_1.datatype = 'geojson-feature-collection'::text)))) > 0 AND n.datatype = 'geojson-feature-collection'::text;

CREATE INDEX mv_geojson_geoms_gix ON mv_geojson_geoms USING GIST (geom);
