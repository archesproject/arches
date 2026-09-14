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

-- Vector tiles for the default "streets" basemap, served free of charge by
-- Maptoolkit (https://www.maptoolkit.org/) under their Community License,
-- built from OpenStreetMap data. MAPLIBRE_GLYPHS/MAPLIBRE_SPRITES system
-- settings must point at Maptoolkit-compatible font/sprite services for
-- this basemap's labels and icons to render.
INSERT INTO map_sources(name, source)
    VALUES ('mtk', '{
            "type": "vector",
            "url": "https://tiles.maptoolkit.org/mtk.json",
            "maxzoom": 15,
            "attribution": "\u00a9 <a href=\"https://www.maptoolkit.com/copyright/\" target=\"_blank\">Maptoolkit</a> \u00a9 <a href=\"https://www.openstreetmap.org/copyright\" target=\"_blank\">OpenStreetMap</a> contributors"
        }
    ');

INSERT INTO map_sources(name, source)
    VALUES ('naturalearth', '{
            "type": "raster",
            "url": "https://tiles.maptoolkit.org/naturalearth.json"
        }
    ');

INSERT INTO map_sources(name, source)
    VALUES ('bathymetry_vector', '{
            "type": "vector",
            "url": "https://tiles.maptoolkit.org/bathymetry.json",
            "maxzoom": 12
        }
    ');

INSERT INTO map_sources(name, source)
    VALUES ('rgb-tiles-blur-min', '{
            "type": "raster-dem",
            "url": "https://tiles.maptoolkit.org/terrainrgb.json",
            "maxzoom": 15,
            "encoding": "terrarium",
            "tileSize": 2048
        }
    ');

INSERT INTO map_sources(name, source)
    VALUES ('rgb-tiles-blur-med', '{
            "type": "raster-dem",
            "url": "https://tiles.maptoolkit.org/terrainrgb.json",
            "maxzoom": 15,
            "encoding": "terrarium",
            "tileSize": 4096
        }
    ');

INSERT INTO map_sources(name, source)
    VALUES ('rgb-tiles-blur-max', '{
            "type": "raster-dem",
            "url": "https://tiles.maptoolkit.org/terrainrgb.json",
            "maxzoom": 15,
            "encoding": "terrarium",
            "tileSize": 8192
        }
    ');

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
    VALUES (public.uuid_generate_v1mc(), 'streets', '[{"id":"background","type":"background","minzoom":0,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"background-color":["interpolate",["linear"],["zoom"],11,"hsla(120, 11%, 95%, 1)",14,"hsla(120, 0%, 95%, 1)"]}},{"id":"naturalearth","source":"naturalearth","type":"raster","minzoom":0,"maxzoom":5,"layout":{"visibility":"visible"},"paint":{"raster-opacity":["interpolate",["linear"],["zoom"],3,0.8,5,0.1],"raster-saturation":["interpolate",["linear"],["zoom"],2,-0.36,7,0.14],"raster-brightness-min":0.1,"raster-brightness-max":1,"raster-hue-rotate":25}},{"id":"water_ocean","source":"mtk","source-layer":"water","type":"fill","filter":["==",["get","type"],"ocean"],"minzoom":0,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"fill-color":"hsla(190, 50%, 85%, 1)"}},{"id":"nature_landuse","source":"mtk","source-layer":"landuse","type":"fill","minzoom":5,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"fill-color":["interpolate",["exponential",1.5],["zoom"],4,["match",["get","type"],"quarry","hsla(63.75, 0%, 93%, 0)",["park","cemetery"],"hsla(120, 19%, 93%, 0)","parking","hsla(86.25, 34%, 90%, 0)",["school","hospital"],"hsla(75, 39%, 97%, 0)","pitch","hsla(176.25, 34%, 90%, 0)","flowerbed","hsla(86.25, 54%, 97%, 0)","hsla(75, 0%, 92%, 0)"],5,["match",["get","type"],"quarry","hsla(63.75, 0%, 93%, 1)",["park","cemetery"],"hsla(120, 19%, 93%, 1)","parking","hsla(86.25, 34%, 90%, 1)",["school","hospital"],"hsla(75, 39%, 97%, 1)","pitch","hsla(176.25, 34%, 90%, 1)","flowerbed","hsla(86.25, 54%, 97%, 1)","hsla(75, 0%, 92%, 1)"],14.5,["match",["get","type"],"quarry","hsla(63.75, 0%, 90%, 1)",["park","cemetery"],"hsla(120, 19%, 90%, 1)","parking","hsla(86.25, 34%, 87%, 1)",["school","hospital"],"hsla(75, 39%, 94%, 1)","pitch","hsla(176.25, 34%, 87%, 1)","flowerbed","hsla(86.25, 54%, 94%, 1)","hsla(75, 0%, 97%, 1)"]]}},{"id":"nature_pedestrian","source":"mtk","source-layer":"road","type":"fill","filter":["all",["==",["geometry-type"],"Polygon"],["in",["get","subtype"],["literal",["pedestrian","platform"]]],["!",["has","indoor"]]],"minzoom":11,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"fill-color":["interpolate",["exponential",1.5],["zoom"],5,"hsla(75, 39%, 94%, 1)",14.5,"hsla(75, 39%, 92%, 1)"]}},{"id":"nature_natural","source":"mtk","source-layer":"natural","type":"fill","filter":["all",["==",["geometry-type"],"Polygon"],["!",["in",["get","type"],["literal",["land","protected_area","national_park","aboriginal_lands","military"]]]]],"minzoom":4,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"fill-antialias":false,"fill-color":["interpolate",["linear"],["zoom"],4,["match",["get","type"],"wood","hsla(131.25, 14%, 85%, 0)","farmland","hsla(97.5, 34%, 90%, 0)",["wetland","tidalflat"],"hsla(142.25, 19%, 90%, 0)","rock","hsla(108.75, 0%, 93%, 0)","sand","hsla(75, 39%, 90%, 0)","scrub","hsla(125.63, 14%, 85%, 0)","fell","hsla(108.75, 24%, 87%, 0)","ice","hsla(221.25, 44%, 98%, 0)","salt_desert","hsla(221.25, 29%, 98%, 0)","hsla(120, 24%, 90%, 0)"],5,["match",["get","type"],"wood","hsla(131.25, 14%, 85%, 1)","farmland","hsla(97.5, 34%, 90%, 1)",["wetland","tidalflat"],"hsla(142.25, 19%, 90%, 1)","rock","hsla(108.75, 0%, 93%, 1)","sand","hsla(75, 39%, 90%, 1)","scrub","hsla(125.63, 14%, 85%, 1)","fell","hsla(108.75, 24%, 87%, 1)","ice","hsla(221.25, 44%, 98%, 1)","salt_desert","hsla(221.25, 29%, 98%, 1)","hsla(120, 24%, 90%, 1)"],12,["match",["get","type"],"wood","hsla(131.25, 14%, 82%, 1)","farmland","hsla(97.5, 34%, 87%, 1)",["wetland","tidalflat"],"hsla(142.25, 19%, 87%, 1)","rock","hsla(108.75, 0%, 90%, 1)","sand","hsla(75, 39%, 87%, 1)","scrub","hsla(125.63, 14%, 82%, 1)","fell","hsla(108.75, 24%, 84%, 1)","ice","hsla(221.25, 44%, 95%, 1)","salt_desert","hsla(221.25, 29%, 95%, 1)","hsla(120, 24%, 87%, 1)"]]}},{"id":"water_lagoon","source":"mtk","source-layer":"water","type":"fill","filter":["all",["==",["geometry-type"],"Polygon"],["in",["get","type"],["literal",["harbour","lagoon"]]]],"minzoom":0,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"fill-color":"hsla(190, 50%, 80%, 0.7)"}},{"id":"relief_ambient_occlusion_blur_min_hillshade","type":"hillshade","paint":{"hillshade-exaggeration":["interpolate",["linear"],["zoom"],5,0.2,16,0.3],"hillshade-shadow-color":"hsla(203, 0%, 0%, 0.3)","hillshade-accent-color":"hsla(203, 0%, 0%, 0)","hillshade-highlight-color":"hsla(44, 100%, 85%, 0)"},"layout":{"visibility":"visible"},"source":"rgb-tiles-blur-min","maxzoom":22,"minzoom":0},{"id":"relief_ambient_occlusion_blur_med_hillshade","type":"hillshade","paint":{"hillshade-exaggeration":["interpolate",["linear"],["zoom"],5,0.2,16,0.3],"hillshade-shadow-color":"hsla(203, 0%, 30%, 0.3)","hillshade-accent-color":"hsla(203, 0%, 0%, 0)","hillshade-highlight-color":"hsla(44, 100%, 85%, 0)"},"layout":{"visibility":"visible"},"source":"rgb-tiles-blur-med","maxzoom":22,"minzoom":0},{"id":"relief_ambient_occlusion_blur_max_hillshade","type":"hillshade","paint":{"hillshade-exaggeration":["interpolate",["linear"],["zoom"],5,0.2,16,0.3],"hillshade-shadow-color":"hsla(203, 0%, 60%, 0.3)","hillshade-accent-color":"hsla(203, 0%, 0%, 0)","hillshade-highlight-color":"hsla(44, 100%, 85%, 0)"},"layout":{"visibility":"visible"},"source":"rgb-tiles-blur-max","maxzoom":22,"minzoom":0},{"id":"water_waterway","source":"mtk","source-layer":"water","type":"line","filter":["all",["==",["geometry-type"],"LineString"],["!=",["get","crossing"],"tunnel"],["!=",["get","intermittent"],1]],"minzoom":0,"maxzoom":22,"layout":{"line-cap":"round","visibility":"visible"},"paint":{"line-color":"hsla(201.25, 55%, 75%, 1)","line-width":["interpolate",["exponential",1.2],["zoom"],3,["match",["get","type"],"river",1,["stream","canal"],0.5,0.33],19,["match",["get","type"],"river",6,["stream","canal"],3,1.98]]}},{"id":"border_protected_area_band","source":"mtk","source-layer":"natural","type":"line","filter":["in",["get","type"],["literal",["national_park","aboriginal_lands"]]],"minzoom":4,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"line-opacity":["interpolate",["exponential",0.9],["zoom"],8,0,10,0.2],"line-color":["interpolate",["exponential",0.9],["zoom"],8,["match",["get","type"],"aboriginal_lands","hsla(95.5, 35%, 48%, 1)","military","hsla(45, 5%, 65%, 1)","hsla(-180, 15%, 40%, 1)"],10,["match",["get","type"],"aboriginal_lands","hsla(95.5, 65%, 48%, 1)","military","hsla(45, 35%, 65%, 1)","hsla(-180, 45%, 40%, 1)"]],"line-width":["interpolate",["exponential",0.9],["zoom"],3,["match",["get","type"],"national_park",1,0.66],19,["match",["get","type"],"national_park",6,3.96]],"line-offset":["interpolate",["exponential",0.9],["zoom"],3,["match",["get","type"],"national_park",0.5,0.33],19,["match",["get","type"],"national_park",3,1.98]]}},{"id":"water_intermittent","source":"mtk","source-layer":"water","type":"fill","filter":["all",["==",["geometry-type"],"Polygon"],["==",["get","intermittent"],1]],"minzoom":0,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"fill-color":"hsla(190, 50%, 96%, 1)"}},{"id":"water_intermittent_outline","source":"mtk","source-layer":"water","type":"line","filter":["==",["get","intermittent"],1],"minzoom":0,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"line-color":"hsla(201.25, 55%, 75%, 1)","line-width":["interpolate",["exponential",1.2],["zoom"],3,["match",["get","type"],"river",1,["lake","stream","canal"],0.5,0.33],19,["match",["get","type"],"river",6,["lake","stream","canal"],3,1.98]],"line-dasharray":[3,3]}},{"id":"water_inland","source":"mtk","source-layer":"water","type":"fill","filter":["all",["==",["geometry-type"],"Polygon"],["!=",["get","intermittent"],1],["!",["in",["get","type"],["literal",["ocean","harbour","lagoon"]]]]],"minzoom":0,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"fill-color":"hsla(190, 50%, 80%, 1)"}},{"id":"water_bathymetry_vector","type":"fill","paint":{"fill-color":["match",["get","depth"],2,"hsla(190, 50%, 84%, 1)",5,"hsla(190, 50%, 82%, 1)",10,"hsla(190, 50%, 80%, 1)",15,"hsla(190, 50%, 78%, 1)",20,"hsla(190, 50%, 76%, 1)",25,"hsla(190, 50%, 74%, 1)",50,"hsla(190, 50%, 72%, 1)",100,"hsla(190, 50%, 70%, 1)",250,"hsla(190, 50%, 68%, 1)",500,"hsla(190, 50%, 66%, 1)",1000,"hsla(190, 50%, 64%, 1)",5000,"hsla(190, 50%, 62%, 1)","hsla(190, 50%, 60%, 1)"]},"layout":{"visibility":"visible","fill-sort-key":["get","depth"]},"source":"bathymetry_vector","maxzoom":22,"minzoom":0,"source-layer":"bathymetry"},{"id":"border_admin_band_province","source":"mtk","source-layer":"admin","type":"line","filter":["all",["in",["get","admin_level"],["literal",[4,3]]],["==",["get","disputed"],0],["==",["get","maritime"],0]],"minzoom":4,"maxzoom":22,"layout":{"line-cap":"round","line-join":"round","visibility":"visible"},"paint":{"line-opacity":["interpolate",["exponential",0.9],["zoom"],10,0.6,13,0.5],"line-color":"hsla(0, 0%, 93%, 1)","line-width":["interpolate",["exponential",0.9],["zoom"],4,1.98,19,7.92],"line-blur":["interpolate",["exponential",0.9],["zoom"],4,0.4,19,1.58]}},{"id":"border_admin_band_country","source":"mtk","source-layer":"admin","type":"line","filter":["all",["==",["get","admin_level"],2],["==",["get","disputed"],0],["==",["get","maritime"],0]],"minzoom":4,"maxzoom":22,"layout":{"line-cap":"round","line-join":"round","visibility":"visible"},"paint":{"line-opacity":["interpolate",["exponential",0.9],["zoom"],10,0.6,13,0.5],"line-color":"hsla(0, 0%, 93%, 1)","line-width":["interpolate",["exponential",0.9],["zoom"],4,3,19,12],"line-blur":["interpolate",["exponential",0.9],["zoom"],4,0.6,19,2.4]}},{"id":"border_admin_band_disputed","source":"mtk","source-layer":"admin","type":"line","filter":["all",["==",["get","admin_level"],2],["==",["get","disputed"],1],["==",["get","maritime"],0]],"minzoom":4,"maxzoom":22,"layout":{"line-cap":"round","line-join":"round","visibility":"visible"},"paint":{"line-opacity":["interpolate",["exponential",0.9],["zoom"],10,0.6,13,0.5],"line-color":"hsla(0, 0%, 93%, 1)","line-width":["interpolate",["exponential",0.9],["zoom"],4,3,19,12],"line-blur":["interpolate",["exponential",0.9],["zoom"],4,0.6,19,2.4]}},{"id":"border_protected_area","source":"mtk","source-layer":"natural","type":"line","filter":["in",["get","type"],["literal",["national_park","aboriginal_lands"]]],"minzoom":4,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"line-color":["interpolate",["exponential",0.9],["zoom"],8,["match",["get","type"],"aboriginal_lands","hsla(95.5, 35%, 48%, 0.5)","military","hsla(45, 5%, 65%, 0.5)","hsla(-180, 15%, 40%, 0.5)"],10,["match",["get","type"],"aboriginal_lands","hsla(95.5, 65%, 48%, 0.6)","military","hsla(45, 35%, 65%, 0.5)","hsla(-180, 45%, 40%, 0.6)"]],"line-width":["interpolate",["exponential",0.9],["zoom"],3,["match",["get","type"],"national_park",0.25,0.17],19,["match",["get","type"],"national_park",1.5,0.99]]}},{"id":"border_admin_province","source":"mtk","source-layer":"admin","type":"line","filter":["all",["in",["get","admin_level"],["literal",[4,3]]],["==",["get","disputed"],0],["==",["get","maritime"],0]],"minzoom":0,"maxzoom":22,"layout":{"line-cap":"round","line-join":"round","visibility":"visible"},"paint":{"line-dasharray":[1,0],"line-color":"hsla(0, 0%, 65%, 1)","line-width":["interpolate",["exponential",0.9],["zoom"],3,0.33,19,1.98]}},{"id":"border_admin_country","source":"mtk","source-layer":"admin","type":"line","filter":["all",["==",["get","admin_level"],2],["==",["get","disputed"],0],["==",["get","maritime"],0]],"minzoom":0,"maxzoom":22,"layout":{"line-cap":"round","line-join":"round","visibility":"visible"},"paint":{"line-dasharray":[1,0],"line-color":"hsla(0, 0%, 55%, 1)","line-width":["interpolate",["exponential",0.9],["zoom"],3,0.5,19,3]}},{"id":"border_admin_disputed","source":"mtk","source-layer":"admin","type":"line","filter":["all",["==",["get","admin_level"],2],["==",["get","disputed"],1],["==",["get","maritime"],0]],"minzoom":0,"maxzoom":22,"layout":{"line-cap":"round","line-join":"round","visibility":"visible"},"paint":{"line-color":"hsla(0, 0%, 55%, 1)","line-dasharray":[1,3],"line-width":["interpolate",["exponential",0.9],["zoom"],3,0.5,19,3]}},{"id":"road_walls_area_shadow","source":"mtk","source-layer":"road","type":"line","filter":["all",["==",["geometry-type"],"Polygon"],["==",["get","type"],"citywalls"]],"minzoom":15,"maxzoom":22,"layout":{"line-cap":"butt","line-join":"round","visibility":"visible"},"paint":{"line-blur":["interpolate",["exponential",1.6],["zoom"],6,0.11,19,17.96],"line-opacity":["interpolate",["exponential",1.6],["zoom"],15,0,17,0.3],"line-color":"hsla(45, 20%, 40%, 1)","line-width":["interpolate",["exponential",1.6],["zoom"],6,0.24,19,16.68]}},{"id":"road_walls_shadow","source":"mtk","source-layer":"road","type":"line","filter":["all",["==",["geometry-type"],"LineString"],["in",["get","type"],["literal",["citywalls","pier"]]]],"minzoom":13,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"line-opacity":["interpolate",["exponential",1.6],["zoom"],15,0,17,0.3],"line-color":"hsla(45, 20%, 40%, 1)","line-width":["interpolate",["exponential",1.6],["zoom"],6,0.24,19,16.68],"line-blur":["interpolate",["exponential",1.6],["zoom"],6,0.11,19,17.96],"line-gap-width":["interpolate",["exponential",1.6],["zoom"],6,0.7,19,4.3]}},{"id":"building_shadow","source":"mtk","source-layer":"building","type":"line","filter":["!=",["get","building"],"roof"],"minzoom":15,"maxzoom":22,"layout":{"line-cap":"butt","line-join":"round","visibility":"visible"},"paint":{"line-blur":["interpolate",["exponential",1.6],["zoom"],6,0.11,19,17.96],"line-opacity":["interpolate",["exponential",1.6],["zoom"],15,0,17,0.3],"line-color":"hsla(45, 20%, 40%, 1)","line-width":["interpolate",["exponential",1.6],["zoom"],6,0.24,19,16.68]}},{"id":"road_walls_base","source":"mtk","source-layer":"road","type":"fill","filter":["all",["==",["geometry-type"],"Polygon"],["==",["get","type"],"citywalls"]],"minzoom":13,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"fill-color":"hsla(75, 0%, 97%, 1)"}},{"id":"building_base","source":"mtk","source-layer":"building","type":"fill","filter":["!=",["get","building"],"roof"],"minzoom":13,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"fill-color":"hsla(75, 0%, 97%, 1)"}},{"id":"road_minor_blur","source":"mtk","source-layer":"road","type":"line","filter":["all",["==",["geometry-type"],"LineString"],["in",["get","type"],["literal",["raceway","minor","service","track"]]],["!",["has","crossing"]]],"minzoom":12,"maxzoom":22,"layout":{"line-cap":"round","line-join":"round","visibility":"visible"},"paint":{"line-blur":["interpolate",["exponential",1.6],["zoom"],6,["match",["get","type"],"minor",0.28,0.16],19,["match",["get","type"],"minor",18.55,10.5]],"line-opacity":0.5,"line-color":["interpolate",["linear"],["zoom"],12,"hsla(22, 75%, 98%, 1)",14,["match",["get","type"],["raceway","minor","service"],"hsla(22, 75%, 81%, 1)","hsla(22, 75%, 98%, 1)"]],"line-width":["interpolate",["exponential",1.6],["zoom"],6,["match",["get","type"],"minor",0.95,0.54],19,["match",["get","type"],"minor",61.82,34.99]]}},{"id":"road_major_blur","source":"mtk","source-layer":"road","type":"line","filter":["all",["in",["get","type"],["literal",["tertiary","secondary","primary","trunk","motorway"]]],["!",["has","crossing"]]],"minzoom":12,"maxzoom":22,"layout":{"line-cap":"round","line-join":"round","visibility":"visible"},"paint":{"line-blur":["interpolate",["exponential",1.6],["zoom"],6,["case",["==",["get","ramp"],1],0.28,["match",["get","type"],"tertiary",0.37,"secondary",0.4,"primary",0.42,"trunk",0.48,0.54]],19,["case",["==",["get","ramp"],1],18.55,["match",["get","type"],"tertiary",23.79,"secondary",25.89,"primary",27.64,"trunk",31.14,34.99]]],"line-opacity":0.5,"line-color":["interpolate",["linear"],["zoom"],12,"hsla(22, 75%, 98%, 1)",14,"hsla(22, 75%, 81%, 1)"],"line-width":["interpolate",["exponential",1.6],["zoom"],6,["case",["==",["get","ramp"],1],0.95,["match",["get","type"],"tertiary",1.22,"secondary",1.33,"primary",1.42,"trunk",1.6,1.79]],19,["case",["==",["get","ramp"],1],61.82,["match",["get","type"],"tertiary",79.32,"secondary",86.31,"primary",92.15,"trunk",103.81,116.64]]]}},{"id":"road_minor_blur_tunnel","source":"mtk","source-layer":"road","type":"line","filter":["all",["==",["geometry-type"],"LineString"],["in",["get","type"],["literal",["raceway","minor","service","track"]]],["==",["get","crossing"],"tunnel"]],"minzoom":11,"maxzoom":22,"layout":{"line-cap":"round","line-join":"round","visibility":"visible"},"paint":{"line-blur":["interpolate",["exponential",1.6],["zoom"],6,["match",["get","type"],"minor",0.28,0.16],19,["match",["get","type"],"minor",18.55,10.5]],"line-opacity":0.5,"line-color":"hsla(22, 75%, 98%, 1)","line-width":["interpolate",["exponential",1.6],["zoom"],6,["match",["get","type"],"minor",0.95,0.54],19,["match",["get","type"],"minor",61.82,34.99]]}},{"id":"road_major_blur_tunnel","source":"mtk","source-layer":"road","type":"line","filter":["all",["in",["get","type"],["literal",["tertiary","secondary","primary","trunk","motorway"]]],["==",["get","crossing"],"tunnel"]],"minzoom":4,"maxzoom":22,"layout":{"line-cap":"round","line-join":"round","visibility":"visible"},"paint":{"line-blur":["interpolate",["exponential",1.6],["zoom"],6,["case",["==",["get","ramp"],1],0.28,["match",["get","type"],"tertiary",0.37,"secondary",0.4,"primary",0.42,"trunk",0.48,0.54]],19,["case",["==",["get","ramp"],1],18.55,["match",["get","type"],"tertiary",23.79,"secondary",25.89,"primary",27.64,"trunk",31.14,34.99]]],"line-opacity":0.5,"line-color":"hsla(22, 75%, 98%, 1)","line-width":["interpolate",["exponential",1.6],["zoom"],6,["case",["==",["get","ramp"],1],0.95,["match",["get","type"],"tertiary",1.22,"secondary",1.33,"primary",1.42,"trunk",1.6,1.79]],19,["case",["==",["get","ramp"],1],61.82,["match",["get","type"],"tertiary",79.32,"secondary",86.31,"primary",92.15,"trunk",103.81,116.64]]]}},{"id":"road_minor_casing_tunnel","source":"mtk","source-layer":"road","type":"line","filter":["all",["in",["get","type"],["literal",["raceway","minor","track"]]],["has","crossing"],["==",["get","crossing"],"tunnel"]],"minzoom":11,"maxzoom":22,"layout":{"line-cap":"butt","line-join":"round","visibility":"visible"},"paint":{"line-color":["interpolate",["linear"],["zoom"],11,"hsla(22, 50%, 48%, 0.2)",14,"hsla(22, 50%, 48%, 0.7)"],"line-gap-width":["interpolate",["exponential",1.6],["zoom"],6,["match",["get","type"],"minor",0.47,0.27],19,["match",["get","type"],"minor",30.91,17.5]],"line-width":["interpolate",["exponential",1.6],["zoom"],6,0.67,19,1.25]}},{"id":"road_major_casing_tunnel","source":"mtk","source-layer":"road","type":"line","filter":["all",["in",["get","type"],["literal",["tertiary","secondary","primary","trunk","motorway"]]],["has","crossing"],["==",["get","crossing"],"tunnel"]],"minzoom":5,"maxzoom":22,"layout":{"line-cap":"butt","line-join":"round","visibility":"visible"},"paint":{"line-color":["interpolate",["linear"],["zoom"],10,"hsla(22, 50%, 48%, 0.2)",13,"hsla(22, 50%, 48%, 0.7)"],"line-gap-width":["interpolate",["exponential",1.6],["zoom"],6,["case",["==",["get","ramp"],1],0.47,["match",["get","type"],"tertiary",0.61,"secondary",0.66,"primary",0.71,"trunk",0.8,0.9]],19,["case",["==",["get","ramp"],1],30.91,["match",["get","type"],"tertiary",39.66,"secondary",43.16,"primary",46.07,"trunk",51.9,58.32]]],"line-width":["interpolate",["exponential",1.6],["zoom"],6,0.71,19,1.33]}},{"id":"road_rail_tunnel","source":"mtk","source-layer":"road","type":"line","filter":["all",["==",["get","type"],"railway"],["==",["get","crossing"],"tunnel"]],"minzoom":6,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"line-color":["interpolate",["linear"],["zoom"],6,"hsla(202, 80%, 68%, 1)",14,["case",["has","service"],"hsla(202, 60%, 48%, 0)",["in",["get","subtype"],["literal",["subway","funicular"]]],"hsla(202, 80%, 48%, 0)","hsla(202, 80%, 48%, 1)"],15,["case",["in",["get","subtype"],["literal",["tram","miniature","monorail","preserved"]]],"hsla(202, 80%, 48%, 0)",["has","service"],"hsla(202, 60%, 48%, 1)","hsla(202, 80%, 48%, 1)"],16,["case",["has","service"],"hsla(202, 60%, 48%, 1)","hsla(202, 80%, 48%, 1)"]],"line-width":["interpolate",["exponential",1.2],["zoom"],6,["case",["any",["has","service"],["in",["get","subtype"],["literal",["tram","subway","miniature","funicular","monorail","preserved"]]]],0.19,0.38],19,3.63],"line-dasharray":[4,3]}},{"id":"road_walls_casing","source":"mtk","source-layer":"road","type":"line","filter":["all",["==",["geometry-type"],"LineString"],["in",["get","type"],["literal",["citywalls","pier"]]]],"minzoom":13,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"line-color":"hsla(45, 5%, 77%, 1)","line-width":["interpolate",["exponential",1.6],["zoom"],6,0.62,19,1.15],"line-gap-width":["interpolate",["exponential",1.6],["zoom"],6,0.27,19,17.5]}},{"id":"road_walls","source":"mtk","source-layer":"road","type":"line","filter":["all",["==",["geometry-type"],"LineString"],["in",["get","type"],["literal",["citywalls","pier"]]]],"minzoom":13,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"line-color":"hsla(45, 18%, 92%, 1)","line-width":["interpolate",["exponential",1.6],["zoom"],6,0.27,19,17.5]}},{"id":"road_walls_area","source":"mtk","source-layer":"road","type":"fill","filter":["all",["==",["geometry-type"],"Polygon"],["in",["get","type"],["literal",["citywalls","pier","dam"]]]],"minzoom":13,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"fill-color":"hsla(45, 18%, 92%, 0.5)","fill-outline-color":"hsla(45, 5%, 77%, 0.5)"}},{"id":"road_minor_casing","source":"mtk","source-layer":"road","type":"line","filter":["all",["==",["geometry-type"],"LineString"],["!=",["get","subtype"],"pedestrian"],["in",["get","type"],["literal",["track","service","raceway","minor"]]],["!",["has","crossing"]]],"minzoom":13,"maxzoom":22,"layout":{"line-cap":"butt","line-join":"round","visibility":"visible"},"paint":{"line-color":["interpolate",["linear"],["zoom"],13,"hsla(22, 50%, 98%, 0)",15,"hsla(22, 50%, 98%, 0.3)",16,"hsla(22, 50%, 48%, 1)"],"line-gap-width":["interpolate",["exponential",1.6],["zoom"],6,["match",["get","type"],"minor",0.47,0.27],19,["match",["get","type"],"minor",30.91,17.5]],"line-width":["interpolate",["exponential",1.6],["zoom"],6,0.67,19,1.25]}},{"id":"road_major_casing","source":"mtk","source-layer":"road","type":"line","filter":["all",["in",["get","type"],["literal",["tertiary","secondary","primary","trunk","motorway"]]],["!",["has","crossing"]]],"minzoom":5,"maxzoom":22,"layout":{"line-cap":"butt","line-join":"round","visibility":"visible"},"paint":{"line-color":["interpolate",["linear"],["zoom"],5,"hsla(22, 50%, 98%, 0.3)",9,["match",["get","type"],"motorway","hsla(22, 50%, 98%, 1)",["trunk","primary"],"hsla(22, 50%, 98%, 0.7)","hsla(22, 50%, 98%, 0)"],10,["match",["get","type"],["motorway","trunk","primary"],"hsla(22, 50%, 98%, 1)","hsla(22, 50%, 98%, 0)"],13,["case",["any",["==",["get","ramp"],1],["in",["get","type"],["literal",["secondary","tertiary"]]]],"hsla(22, 50%, 98%, 1)","hsla(22, 50%, 98%, 1)"],16,"hsla(22, 50%, 48%, 1)"],"line-gap-width":["interpolate",["exponential",1.6],["zoom"],6,["case",["==",["get","ramp"],1],0.47,["match",["get","type"],"tertiary",0.61,"secondary",0.66,"primary",0.71,"trunk",0.8,0.9]],19,["case",["==",["get","ramp"],1],30.91,["match",["get","type"],"tertiary",39.66,"secondary",43.16,"primary",46.07,"trunk",51.9,58.32]]],"line-width":["interpolate",["exponential",1.6],["zoom"],6,0.71,19,1.33]}},{"id":"road_ferry","type":"line","source":"mtk","source-layer":"road","minzoom":4,"maxzoom":22,"filter":["match",["get","type"],["ferry"],true,false],"layout":{"line-join":"round","visibility":"visible"},"paint":{"line-color":"hsla(359, 75%, 98%, 1)","line-dasharray":[2,3],"line-width":["interpolate",["exponential",1.2],["zoom"],6,0.38,19,4.61]}},{"id":"road_light","source":"mtk","source-layer":"road","type":"line","filter":["all",["==",["geometry-type"],"LineString"],["in",["get","type"],["literal",["minor","service","track","raceway","aeroway"]]],["!",["has","crossing"]]],"minzoom":10,"maxzoom":22,"layout":{"line-cap":"round","line-join":"round","visibility":"visible"},"paint":{"line-color":["interpolate",["linear"],["zoom"],10,"hsla(359, 75%, 98%, 0)",11,["case",["==",["get","subtype"],"runway"],"hsla(359, 75%, 98%, 1)","hsla(359, 75%, 98%, 0)"],12,["case",["in",["get","subtype"],["literal",["pedestrian","living_street"]]],"hsla(202, 20%, 88%, 1)",["in",["get","type"],["literal",["minor","service","raceway","aeroway"]]],"hsla(359, 75%, 98%, 1)","hsla(359, 75%, 98%, 0.7)"]],"line-width":["interpolate",["exponential",1.6],["zoom"],6,["case",["any",["==",["get","type"],"minor"],["==",["get","subtype"],"runway"]],0.47,0.27],19,["case",["any",["==",["get","type"],"minor"],["==",["get","subtype"],"runway"]],30.91,17.5]]}},{"id":"road_medium","source":"mtk","source-layer":"road","type":"line","filter":["all",["any",["in",["get","type"],["literal",["tertiary","secondary"]]],["==",["get","ramp"],1]],["!",["has","crossing"]]],"minzoom":9,"maxzoom":22,"layout":{"line-cap":"round","line-join":"round","visibility":"visible"},"paint":{"line-blur":["interpolate",["linear"],["zoom"],16,0,19,["case",["==",["get","ramp"],1],0,["match",["get","type"],"tertiary",0,0]]],"line-color":["interpolate",["linear"],["zoom"],9,"hsla(359, 75%, 78%, 0)",9.5,["match",["get","type"],"secondary","hsla(45, 75%, 78%, 1)","hsla(359, 75%, 78%, 0)"],10.5,"hsla(45, 75%, 78%, 1)"],"line-width":["interpolate",["exponential",1.6],["zoom"],6,["case",["==",["get","ramp"],1],0.47,["match",["get","type"],"tertiary",0.61,0.66]],19,["case",["==",["get","ramp"],1],30.91,["match",["get","type"],"tertiary",39.66,43.16]]]}},{"id":"road_dark","source":"mtk","source-layer":"road","type":"line","filter":["all",["in",["get","type"],["literal",["motorway","trunk","primary"]]],["!=",["get","ramp"],1],["!",["has","crossing"]]],"minzoom":4,"maxzoom":22,"layout":{"line-cap":"round","line-join":"round","visibility":"visible"},"paint":{"line-blur":["interpolate",["linear"],["zoom"],16,0,19,["match",["get","type"],"primary",0,"trunk",0,0]],"line-color":["interpolate",["linear"],["zoom"],4,"hsla(359, 75%, 63%, 0)",6,["match",["get","type"],["primary","trunk"],"hsla(359, 75%, 63%, 0)","hsla(22, 75%, 63%, 1)"],7.5,"hsla(22, 75%, 63%, 1)"],"line-width":["interpolate",["exponential",1.6],["zoom"],6,["match",["get","type"],"primary",0.71,"trunk",0.8,0.9],19,["match",["get","type"],"primary",46.07,"trunk",51.9,58.32]]}},{"id":"road_rail","source":"mtk","source-layer":"road","type":"line","filter":["all",["==",["get","type"],"railway"],["!",["has","crossing"]]],"minzoom":6,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"line-color":["interpolate",["linear"],["zoom"],6,"hsla(202, 80%, 68%, 1)",14,["case",["has","service"],"hsla(202, 60%, 48%, 0)",["in",["get","subtype"],["literal",["subway","funicular"]]],"hsla(202, 80%, 48%, 0)","hsla(202, 80%, 48%, 1)"],15,["case",["in",["get","subtype"],["literal",["tram","miniature","monorail","preserved"]]],"hsla(202, 80%, 48%, 0)",["has","service"],"hsla(202, 60%, 48%, 1)","hsla(202, 80%, 48%, 1)"],16,["case",["has","service"],"hsla(202, 60%, 48%, 1)","hsla(202, 80%, 48%, 1)"]],"line-width":["interpolate",["exponential",1.2],["zoom"],6,["case",["any",["has","service"],["in",["get","subtype"],["literal",["tram","subway","miniature","funicular","monorail","preserved"]]]],0.19,0.38],19,3.63]}},{"id":"road_rail_hatching","source":"mtk","source-layer":"road","type":"line","filter":["all",["==",["get","type"],"railway"],["!",["has","crossing"]]],"minzoom":15,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"line-color":["interpolate",["linear"],["zoom"],15,["case",["in",["get","subtype"],["literal",["tram","subway","miniature","funicular","monorail","preserved"]]],"hsla(202, 60%, 48%, 0)",["has","service"],"hsla(202, 60%, 48%, 1)","hsla(202, 80%, 48%, 1)"],16,["case",["has","service"],"hsla(202, 60%, 48%, 1)","hsla(202, 80%, 48%, 1)"]],"line-dasharray":[0.1,8],"line-width":["interpolate",["exponential",1.2],["zoom"],6,["case",["any",["has","service"],["in",["get","subtype"],["literal",["tram","subway","miniature","funicular","monorail","preserved"]]]],0.75,1.51],19,14.52]}},{"id":"road_bridge","source":"mtk","source-layer":"road","type":"fill","filter":["all",["==",["geometry-type"],"Polygon"],["==",["get","type"],"bridge"]],"minzoom":13,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"fill-color":"hsla(45, 18%, 92%, 0.5)","fill-outline-color":"hsla(45, 5%, 77%, 0.5)"}},{"id":"building_multicolored","source":"mtk","source-layer":"building","type":"fill","minzoom":13,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"fill-color":["case",["has","colour_index"],["interpolate",["linear"],["get","colour_index"],0,"hsla(45, 37%, 88%, 0.5)",5,"hsla(45, 18%, 92%, 0.5)",10,"hsla(45, 22%, 85%, 0.5)"],"hsla(45, 18%, 92%, 0.5)"],"fill-outline-color":"hsla(45, 5%, 77%, 0.5)"}},{"id":"building_3D_multicolored","source":"mtk","source-layer":"building","type":"fill-extrusion","filter":["==","extrude",true],"minzoom":14,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"fill-extrusion-base":["get","min_height"],"fill-extrusion-color":["case",["has","colour_index"],["interpolate",["linear"],["get","colour_index"],0,"hsla(45, 37%, 88%, 1)",5,"hsla(45, 18%, 92%, 1)",10,"hsla(45, 22%, 85%, 1)"],"hsla(45, 22%, 85%, 1)"],"fill-extrusion-height":["get","height"],"fill-extrusion-opacity":["interpolate",["linear"],["zoom"],14,0.2,14.5,0.5],"fill-extrusion-vertical-gradient":true}},{"id":"road_minor_blur_bridge","source":"mtk","source-layer":"road","type":"line","filter":["all",["==",["get","crossing"],"bridge"],["in",["get","type"],["literal",["minor","raceway","service","track"]]],["==",["geometry-type"],"LineString"]],"minzoom":12,"maxzoom":22,"layout":{"line-cap":"butt","line-join":"round","visibility":"visible"},"paint":{"line-blur":["interpolate",["exponential",1.6],["zoom"],6,["match",["get","type"],"minor",0.28,0.16],19,["match",["get","type"],"minor",18.55,10.5]],"line-opacity":0.7,"line-color":"hsla(22, 75%, 38%, 1)","line-width":["interpolate",["exponential",1.6],["zoom"],6,["match",["get","type"],"minor",0.95,0.54],19,["match",["get","type"],"minor",61.82,34.99]]}},{"id":"road_major_blur_bridge","source":"mtk","source-layer":"road","type":"line","filter":["all",["==",["get","crossing"],"bridge"],["in",["get","type"],["literal",["tertiary","secondary","primary","trunk","motorway"]]]],"minzoom":10,"maxzoom":22,"layout":{"line-cap":"butt","line-join":"round","visibility":"visible"},"paint":{"line-blur":["interpolate",["exponential",1.6],["zoom"],6,["case",["==",["get","ramp"],1],0.28,["match",["get","type"],"tertiary",0.37,"secondary",0.4,"primary",0.42,"trunk",0.48,0.54]],19,["case",["==",["get","ramp"],1],18.55,["match",["get","type"],"tertiary",23.79,"secondary",25.89,"primary",27.64,"trunk",31.14,34.99]]],"line-opacity":0.7,"line-color":"hsla(22, 75%, 38%, 1)","line-width":["interpolate",["exponential",1.6],["zoom"],6,["case",["==",["get","ramp"],1],0.95,["match",["get","type"],"tertiary",1.22,"secondary",1.33,"primary",1.42,"trunk",1.6,1.79]],19,["case",["==",["get","ramp"],1],61.82,["match",["get","type"],"tertiary",79.32,"secondary",86.31,"primary",92.15,"trunk",103.81,116.64]]]}},{"id":"road_rail_blur_bridge","source":"mtk","source-layer":"road","type":"line","filter":["all",["==",["get","crossing"],"bridge"],["==",["get","type"],"railway"]],"minzoom":10,"maxzoom":22,"layout":{"line-cap":"butt","line-join":"round","visibility":"visible"},"paint":{"line-blur":["interpolate",["exponential",1.6],["zoom"],6,0.23,19,26.94],"line-opacity":0.5,"line-color":"hsla(22, 75%, 38%, 1)","line-width":["interpolate",["exponential",1.6],["zoom"],6,0.63,19,32.83]}},{"id":"road_minor_casing_bridge","source":"mtk","source-layer":"road","type":"line","filter":["all",["!=",["get","subtype"],"pedestrian"],["in",["get","type"],["literal",["track","service","raceway","minor"]]],["==",["get","crossing"],"bridge"]],"minzoom":13,"maxzoom":22,"layout":{"line-cap":"butt","line-join":"round","visibility":"visible"},"paint":{"line-color":["interpolate",["linear"],["zoom"],13,"hsla(22, 50%, 98%, 0)",15,"hsla(22, 50%, 98%, 0.3)",16,"hsla(22, 50%, 48%, 1)"],"line-gap-width":["interpolate",["exponential",1.6],["zoom"],6,["match",["get","type"],"minor",0.47,0.27],19,["match",["get","type"],"minor",30.91,17.5]],"line-width":["interpolate",["exponential",1.6],["zoom"],6,["match",["get","type"],"minor",0.67,0.62],19,["match",["get","type"],"minor",1.25,1.15]]}},{"id":"road_major_casing_bridge","source":"mtk","source-layer":"road","type":"line","filter":["all",["in",["get","type"],["literal",["tertiary","secondary","primary","trunk","motorway"]]],["==",["get","crossing"],"bridge"]],"minzoom":5,"maxzoom":22,"layout":{"line-cap":"butt","line-join":"round","visibility":"visible"},"paint":{"line-color":["interpolate",["linear"],["zoom"],7,"hsla(22, 50%, 98%, 0.3)",9,["match",["get","type"],"motorway","hsla(22, 50%, 98%, 1)",["trunk","primary"],"hsla(22, 50%, 98%, 0.7)","hsla(22, 50%, 98%, 0)"],10,["match",["get","type"],["motorway","trunk","primary"],"hsla(22, 50%, 98%, 1)","hsla(22, 50%, 98%, 0)"],13,["case",["any",["==",["get","ramp"],1],["in",["get","type"],["literal",["secondary","tertiary"]]]],"hsla(22, 50%, 98%, 1)","hsla(22, 50%, 98%, 1)"],16,"hsla(22, 50%, 48%, 1)"],"line-gap-width":["interpolate",["exponential",1.6],["zoom"],6,["case",["==",["get","ramp"],1],0.47,["match",["get","type"],"tertiary",0.61,"secondary",0.66,"primary",0.71,"trunk",0.8,0.9]],19,["case",["==",["get","ramp"],1],30.91,["match",["get","type"],"tertiary",39.66,"secondary",43.16,"primary",46.07,"trunk",51.9,58.32]]],"line-width":["interpolate",["exponential",1.6],["zoom"],6,["case",["==",["get","ramp"],1],0.67,["match",["get","type"],"tertiary",0.7,"secondary",0.71,"primary",0.71,"trunk",0.72,0.74]],19,["case",["==",["get","ramp"],1],1.25,["match",["get","type"],"tertiary",1.3,"secondary",1.32,"primary",1.33,"trunk",1.36,1.38]]]}},{"id":"road_light_bridge","source":"mtk","source-layer":"road","type":"line","filter":["all",["==",["geometry-type"],"LineString"],["in",["get","type"],["literal",["minor","service","track","raceway","aeroway"]]],["==",["get","crossing"],"bridge"]],"minzoom":10,"maxzoom":22,"layout":{"line-cap":"round","line-join":"round","visibility":"visible"},"paint":{"line-color":["interpolate",["linear"],["zoom"],10,"hsla(359, 75%, 98%, 0)",11,["case",["==",["get","subtype"],"runway"],"hsla(359, 75%, 98%, 1)","hsla(359, 75%, 98%, 0)"],12,["case",["in",["get","subtype"],["literal",["pedestrian","living_street"]]],"hsla(202, 100%, 88%, 1)",["in",["get","type"],["literal",["minor","service","raceway","aeroway"]]],"hsla(359, 75%, 98%, 1)","hsla(359, 75%, 98%, 0.7)"]],"line-width":["interpolate",["exponential",1.6],["zoom"],6,["case",["any",["==",["get","type"],"minor"],["==",["get","subtype"],"runway"]],0.47,0.27],19,["case",["any",["==",["get","type"],"minor"],["==",["get","subtype"],"runway"]],30.91,17.5]]}},{"id":"road_medium_bridge","source":"mtk","source-layer":"road","type":"line","filter":["all",["any",["in",["get","type"],["literal",["tertiary","secondary"]]],["==",["get","ramp"],1]],["==",["get","crossing"],"bridge"]],"minzoom":9,"maxzoom":22,"layout":{"line-cap":"round","line-join":"round","visibility":"visible"},"paint":{"line-blur":["interpolate",["linear"],["zoom"],16,0,19,["case",["==",["get","ramp"],1],0,["match",["get","type"],"tertiary",0,0]]],"line-color":["interpolate",["linear"],["zoom"],9,"hsla(359, 75%, 78%, 0)",9.5,["match",["get","type"],"secondary","hsla(45, 75%, 78%, 1)","hsla(359, 75%, 78%, 0)"],10.5,"hsla(45, 75%, 78%, 1)"],"line-width":["interpolate",["exponential",1.6],["zoom"],6,["case",["==",["get","ramp"],1],0.47,["match",["get","type"],"tertiary",0.61,0.66]],19,["case",["==",["get","ramp"],1],30.91,["match",["get","type"],"tertiary",39.66,43.16]]]}},{"id":"road_dark_bridge","source":"mtk","source-layer":"road","type":"line","filter":["all",["in",["get","type"],["literal",["motorway","trunk","primary"]]],["!=",["get","ramp"],1],["==",["get","crossing"],"bridge"]],"minzoom":4,"maxzoom":22,"layout":{"line-cap":"round","line-join":"round","visibility":"visible"},"paint":{"line-blur":["interpolate",["linear"],["zoom"],16,0,19,["match",["get","type"],"primary",0,"trunk",0,0]],"line-color":["interpolate",["linear"],["zoom"],4,"hsla(359, 75%, 63%, 0)",6,["match",["get","type"],["primary","trunk"],"hsla(359, 75%, 63%, 0)","hsla(22, 75%, 63%, 1)"],7.5,"hsla(22, 75%, 63%, 1)"],"line-width":["interpolate",["exponential",1.6],["zoom"],6,["match",["get","type"],"primary",0.71,"trunk",0.8,0.9],19,["match",["get","type"],"primary",46.07,"trunk",51.9,58.32]]}},{"id":"road_rail_bridge","source":"mtk","source-layer":"road","type":"line","filter":["all",["==",["get","type"],"railway"],["==",["get","crossing"],"bridge"]],"minzoom":6,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"line-color":["interpolate",["linear"],["zoom"],6,"hsla(202, 80%, 68%, 1)",14,["case",["has","service"],"hsla(202, 60%, 48%, 0)",["in",["get","subtype"],["literal",["subway","funicular"]]],"hsla(202, 80%, 48%, 0)","hsla(202, 80%, 48%, 1)"],15,["case",["in",["get","subtype"],["literal",["tram","miniature","monorail","preserved"]]],"hsla(202, 80%, 48%, 0)",["has","service"],"hsla(202, 60%, 48%, 1)","hsla(202, 80%, 48%, 1)"],16,["case",["has","service"],"hsla(202, 60%, 48%, 1)","hsla(202, 80%, 48%, 1)"]],"line-width":["interpolate",["exponential",1.2],["zoom"],6,["case",["any",["has","service"],["in",["get","subtype"],["literal",["tram","subway","miniature","funicular","monorail","preserved"]]]],0.19,0.38],19,3.63]}},{"id":"road_rail_bridge_hatching","source":"mtk","source-layer":"road","type":"line","filter":["all",["==",["get","type"],"railway"],["==",["get","crossing"],"bridge"]],"minzoom":15,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"line-color":["interpolate",["linear"],["zoom"],15,["case",["in",["get","subtype"],["literal",["tram","subway","miniature","funicular","monorail","preserved"]]],"hsla(202, 60%, 48%, 0)",["has","service"],"hsla(202, 60%, 48%, 1)","hsla(202, 80%, 48%, 1)"],16,["case",["has","service"],"hsla(202, 60%, 48%, 1)","hsla(202, 80%, 48%, 1)"]],"line-dasharray":[0.1,8],"line-width":["interpolate",["exponential",1.2],["zoom"],6,["case",["any",["has","service"],["in",["get","subtype"],["literal",["tram","subway","miniature","funicular","monorail","preserved"]]]],0.75,1.51],19,14.52]}},{"id":"road_aerialway","source":"mtk","source-layer":"road","type":"line","filter":["in",["get","subtype"],["literal",["gondola","cable_car","mixed_lift","chair_lift","goods"]]],"minzoom":12,"maxzoom":22,"layout":{"visibility":"visible"},"paint":{"line-color":["interpolate",["linear"],["zoom"],12,"hsla(22, 25%, 38%, 0)",13,"hsla(22, 25%, 38%, 0.7)"],"line-width":["interpolate",["exponential",1.2],["zoom"],6,0.38,19,4.61]}},{"id":"road_goods_lift","type":"line","paint":{"line-color":"hsla(22, 25%, 38%, 0.7)","line-width":4.25,"line-dasharray":[0.3,15]},"filter":["all",["==",["get","type"],"aerialway"],["==",["get","subtype"],"goods"]],"layout":{"line-join":"round","visibility":"visible"},"source":"mtk","source-layer":"road","maxzoom":22,"minzoom":13},{"id":"road_chair_lift","type":"line","paint":{"line-color":["interpolate",["linear"],["zoom"],12,"hsla(22, 25%, 38%, 0)",13,"hsla(22, 25%, 38%, 0.7)"],"line-width":4.75,"line-dasharray":[0.01,8]},"filter":["==",["get","subtype"],"chair_lift"],"layout":{"line-cap":"round","line-join":"round","visibility":"visible"},"source":"mtk","source-layer":"road","maxzoom":22,"minzoom":12},{"id":"road_gondola","type":"line","paint":{"line-color":["interpolate",["linear"],["zoom"],12,"hsla(22, 25%, 38%, 0)",13,"hsla(22, 25%, 38%, 0.7)"],"line-width":2.25,"line-dasharray":[1.5,15],"line-gap-width":2.62},"filter":["in",["get","subtype"],["literal",["gondola","cable_car","mixed_lift"]]],"layout":{"line-cap":"round","line-join":"round","visibility":"visible"},"source":"mtk","source-layer":"road","maxzoom":22,"minzoom":12},{"id":"road_access_no","source":"mtk","source-layer":"road","type":"symbol","filter":["all",["==",["get","access"],"no"],["in",["get","type"],["literal",["minor","raceway","service","track","path","via_ferrata"]]]],"minzoom":15,"maxzoom":22,"layout":{"icon-image":"sdf:no_access","icon-padding":14,"icon-rotation-alignment":"map","icon-rotate":90,"icon-size":["interpolate",["linear"],["zoom"],15,0.41,18,0.54],"symbol-placement":"line","symbol-spacing":80,"visibility":"visible"},"paint":{"icon-color":"hsla(315, 0%, 60%, 1)","icon-halo-color":"hsla(315, 0%, 100%, 1)","icon-halo-width":2}},{"id":"road_minor_oneway_arrows","source":"mtk","source-layer":"road","type":"symbol","filter":["step",["zoom"],["all",["==",["get","oneway"],1],["==",["get","type"],"minor"]],16,["all",["==",["get","oneway"],1],["in",["get","type"],["literal",["minor","raceway","service","track"]]]]],"minzoom":15,"maxzoom":22,"layout":{"icon-image":"sdf:oneway","icon-padding":14,"icon-rotation-alignment":"map","icon-size":["interpolate",["linear"],["zoom"],15,0.49,18,0.65],"symbol-placement":"line","symbol-spacing":250,"visibility":"visible"},"paint":{"icon-color":"hsla(22, 30%, 60%, 1)","icon-halo-color":"hsla(22, 30%, 100%, 1)","icon-halo-width":2}},{"id":"road_major_oneway_arrows","source":"mtk","source-layer":"road","type":"symbol","filter":["all",["==",["get","oneway"],1],["in",["get","type"],["literal",["tertiary","secondary","primary","trunk","motorway"]]]],"minzoom":15,"maxzoom":22,"layout":{"icon-image":"sdf:oneway","icon-padding":14,"icon-rotation-alignment":"map","icon-size":["interpolate",["linear"],["zoom"],15,0.49,18,0.65],"symbol-placement":"line","symbol-spacing":250,"visibility":"visible"},"paint":{"icon-color":"hsla(22, 30%, 60%, 1)","icon-halo-color":"hsla(22, 30%, 100%, 1)","icon-halo-width":2}},{"id":"building_num_label","source":"mtk","source-layer":"housenum_label","type":"symbol","minzoom":17,"maxzoom":22,"layout":{"text-field":["get","housenumber"],"text-font":["literal",["Proza Libre Medium"]],"text-pitch-alignment":"viewport","text-size":["interpolate",["linear"],["zoom"],9,5,16,10.45],"text-padding":["interpolate",["linear"],["zoom"],6,17,16,14],"visibility":"visible"},"paint":{"text-color":"hsla(315, 0%, 70%, 1)","text-halo-color":"hsla(315, 0%, 100%, 0.8)","text-halo-width":0.5}},{"id":"poi_label_symbol_rank_5","source":"mtk","source-layer":"poi_label","type":"symbol","filter":["all",["!",["in",["get","type"],["literal",["peak","mountain_pass","entrance","park","garden","cemetery","drag_lift","tree"]]]],[">",["get","rank_new"],22],["!",["in",["get","category"],["literal",["peak","shop"]]]]],"minzoom":15,"maxzoom":22,"layout":{"symbol-sort-key":["get","rank_new"],"text-anchor":"top","text-justify":"center","text-field":["case",["!",["has","is_nonlatin"]],["get","name"],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]]]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Semibold"]],["literal",["Noto Sans Regular"]]],"text-offset":["literal",[0,0.8]],"text-padding":["interpolate",["linear"],["zoom"],1,20,18,16],"text-pitch-alignment":"viewport","text-size":["interpolate",["linear"],["zoom"],1,["interpolate",["linear"],["get","rank_new"],1,4.89,25,2.15],18,["interpolate",["linear"],["get","rank_new"],1,23.75,25,10.45]],"icon-image":["concat","sdf:",["get","type"]],"icon-padding":["interpolate",["linear"],["zoom"],1,20,18,16],"icon-size":["interpolate",["linear"],["zoom"],7,["interpolate",["linear"],["get","rank_new"],1,0.42,25,0.28],18,["interpolate",["linear"],["get","rank_new"],1,1.31,25,0.87]],"visibility":"visible"},"paint":{"text-color":["match",["get","category"],"religion","hsla(315, 0%, 60%, 1)","food","hsla(315, 10%, 45%, 1)","shop","hsla(315, 0%, 50%, 1)","education","hsla(315, 0%, 60%, 1)","sport","hsla(315, 0%, 40%, 1)","traffic","hsla(315, 0%, 60%, 1)","attraction","hsla(315, 0%, 50%, 1)","health","hsla(315, 10%, 60%, 1)","public","hsla(315, 0%, 60%, 1)","water","hsla(315, 10%, 50%, 1)","hsla(315, 0%, 50%, 1)"],"text-halo-color":["match",["get","category"],"religion","hsla(315, 0%, 100%, 0.8)","food","hsla(315, 10%, 100%, 0.8)","shop","hsla(315, 0%, 100%, 0.8)","education","hsla(315, 0%, 100%, 0.8)","sport","hsla(315, 0%, 100%, 0.8)","traffic","hsla(315, 0%, 100%, 0.8)","attraction","hsla(315, 0%, 100%, 0.8)","health","hsla(315, 10%, 100%, 0.8)","public","hsla(315, 0%, 100%, 0.8)","water","hsla(315, 10%, 100%, 0.8)","hsla(315, 0%, 100%, 0.8)"],"text-halo-width":0.5,"text-halo-blur":0.5,"icon-color":["match",["get","category"],"religion","hsla(315, 0%, 60%, 1)","food","hsla(315, 10%, 45%, 1)","shop","hsla(315, 0%, 50%, 1)","education","hsla(315, 0%, 60%, 1)","sport","hsla(315, 0%, 40%, 1)","traffic","hsla(315, 0%, 60%, 1)","attraction","hsla(315, 0%, 50%, 1)","health","hsla(315, 10%, 60%, 1)","public","hsla(315, 0%, 60%, 1)","water","hsla(315, 10%, 50%, 1)","hsla(315, 0%, 50%, 1)"],"icon-halo-color":["match",["get","category"],"religion","hsla(315, 0%, 100%, 1)","food","hsla(315, 10%, 100%, 1)","shop","hsla(315, 0%, 100%, 1)","education","hsla(315, 0%, 100%, 1)","sport","hsla(315, 0%, 100%, 1)","traffic","hsla(315, 0%, 100%, 1)","attraction","hsla(315, 0%, 100%, 1)","health","hsla(315, 10%, 100%, 1)","public","hsla(315, 0%, 100%, 1)","water","hsla(315, 10%, 100%, 1)","hsla(315, 0%, 100%, 1)"],"icon-halo-width":1.5,"icon-halo-blur":1.5}},{"id":"road_aerialway_label","source":"mtk","source-layer":"road_label","type":"symbol","filter":["in",["get","subtype"],["literal",["gondola","cable_car","chair_lift","goods"]]],"minzoom":14,"maxzoom":22,"layout":{"symbol-placement":"line","symbol-spacing":["interpolate",["linear"],["zoom"],10,100,19,600],"text-field":["case",["has","name"],["get","name"],["get","name"]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Medium"]],["literal",["Noto Sans Regular"]]],"text-pitch-alignment":"viewport","text-size":["interpolate",["linear"],["zoom"],11,7.45,16,12.62],"text-padding":["interpolate",["linear"],["zoom"],6,17,16,14],"visibility":"visible"},"paint":{"text-color":"hsla(315, 0%, 30%, 1)","text-halo-blur":0.5,"text-halo-color":"hsla(315, 0%, 100%, 0.8)","text-halo-width":1}},{"id":"road_rail_label","source":"mtk","source-layer":"road_label","type":"symbol","filter":["in",["get","subtype"],["literal",["rail","narrow_gauge","light_rail","miniature","preserved","funicular"]]],"minzoom":7,"maxzoom":22,"layout":{"symbol-placement":"line","symbol-spacing":["interpolate",["linear"],["zoom"],10,100,19,600],"text-field":["case",["has","name"],["get","name"],["get","name"]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Medium"]],["literal",["Noto Sans Regular"]]],"text-pitch-alignment":"viewport","text-size":["interpolate",["linear"],["zoom"],11,8.28,16,14.02],"text-padding":["interpolate",["linear"],["zoom"],6,17,16,14],"visibility":"visible"},"paint":{"text-color":"hsla(315, 0%, 30%, 1)","text-halo-blur":0.5,"text-halo-color":"hsla(315, 0%, 100%, 0.8)","text-halo-width":1}},{"id":"road_ferry_label","source":"mtk","source-layer":"road_label","type":"symbol","filter":["==",["get","type"],"ferry"],"minzoom":8,"maxzoom":22,"layout":{"symbol-placement":"line","symbol-spacing":["interpolate",["linear"],["zoom"],10,100,19,600],"text-field":["case",["has","name"],["get","name"],["get","name"]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Bold Italic"]],["literal",["Noto Sans Regular"]]],"text-pitch-alignment":"viewport","text-size":["interpolate",["linear"],["zoom"],12,10.22,16,15.58],"text-padding":["interpolate",["linear"],["zoom"],6,17,16,14],"visibility":"visible"},"paint":{"text-color":"hsla(315, 60%, 100%, 1)","text-halo-blur":1.5,"text-halo-color":"hsla(315, 40%, 65%, 1)","text-halo-width":1.5}},{"id":"road_minor_label","source":"mtk","source-layer":"road_label","type":"symbol","filter":["in",["get","type"],["literal",["minor","raceway","track"]]],"minzoom":14,"maxzoom":22,"layout":{"symbol-placement":"line","symbol-spacing":["interpolate",["linear"],["zoom"],10,100,19,600],"text-field":["case",["has","name"],["get","name"],["get","name"]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Medium"]],["literal",["Noto Sans Regular"]]],"text-pitch-alignment":"viewport","text-size":["interpolate",["linear"],["zoom"],11,7.45,16,12.62],"text-padding":["interpolate",["linear"],["zoom"],6,17,16,14],"visibility":"visible"},"paint":{"text-color":"hsla(315, 0%, 30%, 1)","text-halo-blur":0.5,"text-halo-color":"hsla(315, 0%, 100%, 0.8)","text-halo-width":1}},{"id":"water_label_line_rank_5","source":"mtk","source-layer":"water_label","type":"symbol","filter":["all",["==",["geometry-type"],"LineString"],[">",["get","rank"],21],["!=",["get","crossing"],"tunnel"]],"minzoom":14,"maxzoom":22,"layout":{"symbol-sort-key":["get","rank"],"symbol-avoid-edges":false,"symbol-placement":"line","symbol-spacing":["interpolate",["exponential",0.9],["zoom"],1,73,18,1226],"text-field":["case",["!",["has","is_nonlatin"]],["get","name"],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]]]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Italic"]],["literal",["Noto Sans Italic"]]],"text-letter-spacing":["interpolate",["linear"],["zoom"],1,0,18,["interpolate",["exponential",0.95],["get","rank"],1,0.95,25,0]],"text-pitch-alignment":"viewport","text-size":["interpolate",["linear"],["get","rank"],1,26.13,17,13.06],"visibility":"visible"},"paint":{"text-color":"hsla(212.5, 55%, 40%, 1)","text-halo-color":"hsla(212.5, 50%, 100%, 1)","text-halo-width":1,"text-halo-blur":1}},{"id":"water_label_point_rank_5","source":"mtk","source-layer":"water_label","type":"symbol","filter":["all",["==",["geometry-type"],"Point"],[">",["get","rank"],21]],"minzoom":13,"maxzoom":22,"layout":{"symbol-sort-key":["get","rank"],"symbol-placement":"point","text-field":["case",["!",["has","is_nonlatin"]],["get","name"],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]]]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Italic"]],["literal",["Noto Sans Italic"]]],"text-letter-spacing":["interpolate",["linear"],["zoom"],1,0,18,["interpolate",["exponential",0.95],["get","rank"],1,0.71,25,0]],"text-pitch-alignment":"viewport","text-size":["interpolate",["exponential",0.97],["zoom"],1,["interpolate",["linear"],["get","rank"],1,5.87,23,2.35],18,["interpolate",["linear"],["get","rank"],1,28.5,23,11.4]],"text-padding":["interpolate",["linear"],["zoom"],1,20,18,16],"visibility":"visible"},"paint":{"text-color":"hsla(212.5, 55%, 40%, 1)","text-halo-color":"hsla(212.5, 50%, 100%, 1)","text-halo-width":1.5,"text-halo-blur":1.5}},{"id":"place_label_line_rank_5","source":"mtk","source-layer":"place_label","type":"symbol","minzoom":14,"maxzoom":22,"filter":["all",["==",["geometry-type"],"LineString"],[">",["get","rank"],21],["!",["in",["get","category"],["literal",["winter_sports","protected_area","military"]]]]],"layout":{"visibility":"visible","symbol-placement":"line-center","symbol-sort-key":["get","rank"],"symbol-spacing":["interpolate",["exponential",0.9],["zoom"],1,73,18,1226],"text-field":["case",["!",["has","is_nonlatin"]],["get","name"],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]]]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Italic"]],["literal",["Noto Sans Italic"]]],"text-pitch-alignment":"viewport","text-size":["interpolate",["linear"],["get","rank"],1,26.13,17,13.06],"text-letter-spacing":["interpolate",["linear"],["zoom"],1,0,18,["interpolate",["exponential",0.95],["get","rank"],1,0.95,25,0]]},"paint":{"text-color":["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 0%, 1)",25,"hsla(0, 0%, 20%, 1)"],"text-halo-color":["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 85%, 0.8)",25,"hsla(0, 0%, 100%, 0.8)"],"text-halo-width":1,"text-halo-blur":1}},{"id":"place_label_rank_5","source":"mtk","source-layer":"place_label","type":"symbol","minzoom":13,"maxzoom":22,"filter":["all",["==",["geometry-type"],"Point"],[">",["get","rank"],21],["!",["in",["get","category"],["literal",["winter_sports","protected_area","military"]]]]],"layout":{"visibility":"visible","symbol-sort-key":["get","rank"],"text-field":["case",["!",["has","is_nonlatin"]],["get","name"],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]]]],"text-font":["case",["!",["has","is_nonlatin"]],["match",["get","category"],"country",["literal",["Proza Libre Regular"]],"capital",["literal",["Proza Libre Bold"]],"big_place",["literal",["Proza Libre Bold"]],"small_place",["literal",["Proza Libre Medium"]],"other",["literal",["Proza Libre Italic"]],"park",["literal",["Proza Libre Italic"]],["literal",["Proza Libre Bold Italic"]]],["match",["get","category"],"country",["literal",["Noto Sans Regular"]],"capital",["literal",["Noto Sans Bold"]],"big_place",["literal",["Noto Sans Bold"]],"small_place",["literal",["Noto Sans Regular"]],"other",["literal",["Noto Sans Italic"]],"park",["literal",["Noto Sans Italic"]],["literal",["Noto Sans Bold Italic"]]]],"text-pitch-alignment":"viewport","text-transform":["case",["in",["get","category"],["literal",["country","capital"]]],"uppercase","none"],"text-size":["interpolate",["exponential",0.97],["zoom"],1,["interpolate",["linear"],["get","rank"],1,6.36,23,2.35],18,["interpolate",["linear"],["get","rank"],1,30.88,23,11.4]],"text-padding":["interpolate",["linear"],["zoom"],1,20,18,16],"text-letter-spacing":["interpolate",["linear"],["zoom"],1,0,18,["match",["get","category"],["country","other"],["interpolate",["exponential",0.95],["get","rank"],1,0.71,25,0],0]],"text-offset":["literal",[0,-0.2]]},"paint":{"text-color":["match",["get","category"],["national_park","protected_area","park"],"hsla(-180, 35%, 35%, 1)","military","hsla(45, 25%, 60%, 1)","aboriginal_lands","hsla(95.5, 55%, 43%, 1)",["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 0%, 1)",25,"hsla(0, 0%, 20%, 1)"]],"text-halo-color":["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 85%, 0.8)",25,"hsla(0, 0%, 100%, 0.8)"],"text-halo-width":1,"text-halo-blur":1}},{"id":"poi_label_symbol_rank_4","source":"mtk","source-layer":"poi_label","type":"symbol","filter":["all",["!",["in",["get","type"],["literal",["peak","mountain_pass","entrance","park","garden","cemetery","drag_lift","tree"]]]],[">",["get","rank_new"],19],["<=",["get","rank_new"],22],["!",["in",["get","category"],["literal",["peak","shop"]]]]],"minzoom":13,"maxzoom":22,"layout":{"symbol-sort-key":["get","rank_new"],"text-anchor":"top","text-justify":"center","text-field":["case",["!",["has","is_nonlatin"]],["get","name"],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]]]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Semibold"]],["literal",["Noto Sans Regular"]]],"text-offset":["literal",[0,0.8]],"text-padding":["interpolate",["linear"],["zoom"],1,20,18,16],"text-pitch-alignment":"viewport","text-size":["interpolate",["linear"],["zoom"],1,["interpolate",["linear"],["get","rank_new"],1,4.89,25,2.15],18,["interpolate",["linear"],["get","rank_new"],1,23.75,25,10.45]],"icon-image":["concat","sdf:",["get","type"]],"icon-padding":["interpolate",["linear"],["zoom"],1,20,18,16],"icon-size":["interpolate",["linear"],["zoom"],7,["interpolate",["linear"],["get","rank_new"],1,0.42,25,0.28],18,["interpolate",["linear"],["get","rank_new"],1,1.31,25,0.87]],"visibility":"visible"},"paint":{"text-color":["match",["get","category"],"religion","hsla(315, 0%, 60%, 1)","food","hsla(315, 10%, 45%, 1)","shop","hsla(315, 0%, 50%, 1)","education","hsla(315, 0%, 60%, 1)","sport","hsla(315, 0%, 50%, 1)","traffic","hsla(315, 0%, 60%, 1)","attraction","hsla(315, 10%, 50%, 1)","health","hsla(315, 10%, 60%, 1)","public","hsla(315, 0%, 60%, 1)","water","hsla(315, 10%, 50%, 1)","hsla(315, 0%, 45%, 1)"],"text-halo-color":["match",["get","category"],"religion","hsla(315, 0%, 100%, 0.8)","food","hsla(315, 10%, 100%, 0.8)","shop","hsla(315, 0%, 100%, 0.8)","education","hsla(315, 0%, 100%, 0.8)","sport","hsla(315, 0%, 100%, 0.8)","traffic","hsla(315, 0%, 100%, 0.8)","attraction","hsla(315, 10%, 100%, 0.8)","health","hsla(315, 10%, 100%, 0.8)","public","hsla(315, 0%, 100%, 0.8)","water","hsla(315, 10%, 100%, 0.8)","hsla(315, 0%, 100%, 0.8)"],"text-halo-width":0.5,"text-halo-blur":0.5,"icon-color":["match",["get","category"],"religion","hsla(315, 0%, 60%, 1)","food","hsla(315, 10%, 45%, 1)","shop","hsla(315, 0%, 50%, 1)","education","hsla(315, 0%, 60%, 1)","sport","hsla(315, 0%, 50%, 1)","traffic","hsla(315, 0%, 60%, 1)","attraction","hsla(315, 10%, 50%, 1)","health","hsla(315, 10%, 60%, 1)","public","hsla(315, 0%, 60%, 1)","water","hsla(315, 10%, 50%, 1)","hsla(315, 0%, 45%, 1)"],"icon-halo-color":["match",["get","category"],"religion","hsla(315, 0%, 100%, 1)","food","hsla(315, 10%, 100%, 1)","shop","hsla(315, 0%, 100%, 1)","education","hsla(315, 0%, 100%, 1)","sport","hsla(315, 0%, 100%, 1)","traffic","hsla(315, 0%, 100%, 1)","attraction","hsla(315, 10%, 100%, 1)","health","hsla(315, 10%, 100%, 1)","public","hsla(315, 0%, 100%, 1)","water","hsla(315, 10%, 100%, 1)","hsla(315, 0%, 100%, 1)"],"icon-halo-width":1.5,"icon-halo-blur":1.5}},{"id":"road_major_label","source":"mtk","source-layer":"road_label","type":"symbol","filter":["in",["get","type"],["literal",["tertiary","secondary","primary","trunk","motorway"]]],"minzoom":8,"maxzoom":22,"layout":{"symbol-sort-key":["case",["==",["get","type"],"motorway"],1,["==",["get","type"],"trunk"],2,["==",["get","type"],"primary"],3,["==",["get","type"],"secondary"],5,6],"symbol-placement":"line","symbol-spacing":["interpolate",["linear"],["zoom"],10,100,19,600],"text-field":["case",["has","name"],["get","name"],["get","name"]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Medium"]],["literal",["Noto Sans Regular"]]],"text-pitch-alignment":"viewport","text-size":["interpolate",["linear"],["zoom"],11,8.28,16,14.02],"text-padding":["interpolate",["linear"],["zoom"],6,17,16,14],"visibility":"visible"},"paint":{"text-color":"hsla(315, 0%, 30%, 1)","text-halo-blur":0.5,"text-halo-color":"hsla(315, 0%, 100%, 0.8)","text-halo-width":1}},{"id":"water_label_line_rank_4","source":"mtk","source-layer":"water_label","type":"symbol","filter":["all",["==",["geometry-type"],"LineString"],[">",["get","rank"],17],["<=",["get","rank"],21],["!=",["get","crossing"],"tunnel"]],"minzoom":12,"maxzoom":22,"layout":{"symbol-sort-key":["get","rank"],"symbol-avoid-edges":false,"symbol-placement":"line","symbol-spacing":["interpolate",["exponential",0.9],["zoom"],1,73,18,1226],"text-field":["case",["!",["has","is_nonlatin"]],["get","name"],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]]]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Italic"]],["literal",["Noto Sans Italic"]]],"text-letter-spacing":["interpolate",["linear"],["zoom"],1,0,18,["interpolate",["exponential",0.95],["get","rank"],1,0.95,25,0]],"text-pitch-alignment":"viewport","text-size":["interpolate",["exponential",0.97],["zoom"],1,["interpolate",["linear"],["get","rank"],1,5.38,17,2.69],14,["interpolate",["linear"],["get","rank"],1,26.13,17,13.06]],"visibility":"visible"},"paint":{"text-color":"hsla(212.5, 55%, 40%, 1)","text-halo-color":"hsla(212.5, 50%, 100%, 1)","text-halo-width":1,"text-halo-blur":1}},{"id":"water_label_point_rank_4","source":"mtk","source-layer":"water_label","type":"symbol","filter":["all",["==",["geometry-type"],"Point"],[">",["get","rank"],17],["<=",["get","rank"],21]],"minzoom":11,"maxzoom":22,"layout":{"symbol-sort-key":["get","rank"],"symbol-placement":"point","text-field":["case",["!",["has","is_nonlatin"]],["get","name"],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]]]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Italic"]],["literal",["Noto Sans Italic"]]],"text-letter-spacing":["interpolate",["linear"],["zoom"],1,0,18,["interpolate",["exponential",0.95],["get","rank"],1,0.71,25,0]],"text-pitch-alignment":"viewport","text-size":["interpolate",["exponential",0.97],["zoom"],1,["interpolate",["linear"],["get","rank"],1,5.87,23,2.35],18,["interpolate",["linear"],["get","rank"],1,28.5,23,11.4]],"text-padding":["interpolate",["linear"],["zoom"],1,20,18,16],"visibility":"visible"},"paint":{"text-color":"hsla(212.5, 55%, 40%, 1)","text-halo-color":"hsla(212.5, 50%, 100%, 1)","text-halo-width":1.5,"text-halo-blur":1.5}},{"id":"place_label_line_rank_4","source":"mtk","source-layer":"place_label","type":"symbol","minzoom":12,"maxzoom":22,"filter":["all",["==",["geometry-type"],"LineString"],[">",["get","rank"],17],["<=",["get","rank"],21],["!",["in",["get","category"],["literal",["winter_sports","protected_area","military"]]]]],"layout":{"visibility":"visible","symbol-placement":"line-center","symbol-sort-key":["get","rank"],"symbol-spacing":["interpolate",["exponential",0.9],["zoom"],1,73,18,1226],"text-field":["case",["!",["has","is_nonlatin"]],["get","name"],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]]]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Italic"]],["literal",["Noto Sans Italic"]]],"text-pitch-alignment":"viewport","text-size":["interpolate",["exponential",0.97],["zoom"],1,["interpolate",["linear"],["get","rank"],1,5.38,17,2.69],14,["interpolate",["linear"],["get","rank"],1,26.13,17,13.06]],"text-letter-spacing":["interpolate",["linear"],["zoom"],1,0,18,["interpolate",["exponential",0.95],["get","rank"],1,0.95,25,0]]},"paint":{"text-color":["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 0%, 1)",25,"hsla(0, 0%, 20%, 1)"],"text-halo-color":["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 85%, 0.8)",25,"hsla(0, 0%, 100%, 0.8)"],"text-halo-width":1,"text-halo-blur":1}},{"id":"place_label_rank_4","source":"mtk","source-layer":"place_label","type":"symbol","minzoom":10,"maxzoom":22,"filter":["all",["==",["geometry-type"],"Point"],[">",["get","rank"],17],["<=",["get","rank"],21],["!",["in",["get","category"],["literal",["winter_sports","protected_area","military"]]]]],"layout":{"visibility":"visible","symbol-sort-key":["get","rank"],"text-field":["case",["!",["has","is_nonlatin"]],["get","name"],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]]]],"text-font":["case",["!",["has","is_nonlatin"]],["match",["get","category"],"country",["literal",["Proza Libre Regular"]],"capital",["literal",["Proza Libre Bold"]],"big_place",["literal",["Proza Libre Bold"]],"small_place",["literal",["Proza Libre Medium"]],"other",["literal",["Proza Libre Italic"]],"park",["literal",["Proza Libre Italic"]],["literal",["Proza Libre Bold Italic"]]],["match",["get","category"],"country",["literal",["Noto Sans Regular"]],"capital",["literal",["Noto Sans Bold"]],"big_place",["literal",["Noto Sans Bold"]],"small_place",["literal",["Noto Sans Regular"]],"other",["literal",["Noto Sans Italic"]],"park",["literal",["Noto Sans Italic"]],["literal",["Noto Sans Bold Italic"]]]],"text-pitch-alignment":"viewport","text-transform":["case",["in",["get","category"],["literal",["country","capital"]]],"uppercase","none"],"text-size":["interpolate",["exponential",0.97],["zoom"],1,["interpolate",["linear"],["get","rank"],1,6.36,23,2.35],18,["interpolate",["linear"],["get","rank"],1,30.88,23,11.4]],"text-padding":["interpolate",["linear"],["zoom"],1,20,18,16],"text-letter-spacing":["interpolate",["linear"],["zoom"],1,0,18,["match",["get","category"],["country","other"],["interpolate",["exponential",0.95],["get","rank"],1,0.71,25,0],0]],"text-offset":["literal",[0,-0.2]]},"paint":{"text-color":["interpolate",["linear"],["zoom"],1,["match",["get","category"],["national_park","protected_area","park"],"hsla(-180, 35%, 35%, 1)","military","hsla(45, 25%, 60%, 1)","aboriginal_lands","hsla(95.5, 55%, 43%, 1)",["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 20%, 1)",25,"hsla(0, 0%, 40%, 1)"]],13,["match",["get","category"],["national_park","protected_area","park"],"hsla(-180, 35%, 35%, 1)","military","hsla(45, 25%, 60%, 1)","aboriginal_lands","hsla(95.5, 55%, 43%, 1)",["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 0%, 1)",25,"hsla(0, 0%, 20%, 1)"]]],"text-halo-color":["interpolate",["linear"],["zoom"],1,"hsla(0, 0%, 100%, 0.8)",13,["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 85%, 0.8)",25,"hsla(0, 0%, 100%, 0.8)"]],"text-halo-width":1,"text-halo-blur":1}},{"id":"road_label_shield","source":"mtk","source-layer":"road_label","type":"symbol","filter":["all",["in",["get","type"],["literal",["motorway","trunk","primary"]]],["has","ref"]],"minzoom":7,"maxzoom":22,"paint":{"icon-color":"hsla(23, 50%, 70%, 1)","icon-halo-color":"hsla(23, 50%, 100%, 1)","icon-halo-width":1.5,"text-color":"hsla(23, 50%, 100%, 1)"},"layout":{"icon-image":"sdf:square","icon-text-fit":"both","icon-text-fit-padding":["interpolate",["linear"],["zoom"],9,["literal",[3,5,2,5]],16,["literal",[4,7,3,7]]],"icon-rotation-alignment":"viewport","symbol-placement":["step",["zoom"],"point",11,"line"],"symbol-spacing":["interpolate",["linear"],["zoom"],10,200,19,900],"text-field":["get","ref"],"text-font":["literal",["Proza Libre Bold Italic"]],"text-pitch-alignment":"viewport","text-rotation-alignment":"viewport","text-size":["interpolate",["linear"],["zoom"],11,8.28,16,14.02],"text-padding":["interpolate",["linear"],["zoom"],6,17,16,14],"visibility":"visible"}},{"id":"poi_label_street","source":"mtk","source-layer":"poi_label","type":"symbol","filter":["in",["get","type"],["literal",["fuel","charging_station"]]],"minzoom":13,"maxzoom":22,"paint":{"icon-color":"hsla(315, 40%, 60%, 1)","icon-halo-color":"hsla(315, 40%, 100%, 1)","icon-halo-width":1.5,"icon-halo-blur":1.5,"text-color":"hsla(315, 40%, 60%, 1)","text-halo-color":"hsla(315, 40%, 100%, 0.8)","text-halo-width":0.5,"text-halo-blur":0.5},"layout":{"text-anchor":"top","text-justify":"center","text-field":["case",["!",["has","is_nonlatin"]],["get","name"],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]]]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Semibold"]],["literal",["Noto Sans Regular"]]],"text-offset":["literal",[0,0.8]],"text-optional":true,"text-padding":["interpolate",["linear"],["zoom"],1,20,18,16],"text-pitch-alignment":"viewport","text-size":["interpolate",["linear"],["zoom"],1,["interpolate",["linear"],["get","rank_new"],1,4.89,25,2.15],18,["interpolate",["linear"],["get","rank_new"],1,23.75,25,10.45]],"icon-image":["concat","sdf:",["get","type"]],"icon-padding":["interpolate",["linear"],["zoom"],1,20,18,16],"icon-size":["interpolate",["linear"],["zoom"],7,["interpolate",["linear"],["get","rank_new"],1,0.42,25,0.28],18,["interpolate",["linear"],["get","rank_new"],1,1.31,25,0.87]],"visibility":"visible"}},{"id":"road_label_street","source":"mtk","source-layer":"road_label","type":"symbol","filter":["==",["get","subtype"],"junction"],"minzoom":12,"maxzoom":22,"layout":{"symbol-placement":"point","text-field":["case",["all",["has","name"],["has","ref"]],["concat",["get","ref"]," - ",["get","name"]],["coalesce",["get","name"],["get","ref"]]],"text-font":["literal",["Proza Libre Bold Italic"]],"text-pitch-alignment":"viewport","text-size":["interpolate",["linear"],["zoom"],11,8.28,16,14.02],"text-padding":["interpolate",["linear"],["zoom"],6,20,16,16],"visibility":"visible"},"paint":{"text-color":"hsla(22, 90%, 100%, 1)","text-halo-blur":1.5,"text-halo-color":"hsla(22, 90%, 78%, 1)","text-halo-width":1.5}},{"id":"poi_label_symbol_rank_3","source":"mtk","source-layer":"poi_label","type":"symbol","filter":["all",["!",["in",["get","type"],["literal",["peak","mountain_pass","entrance","park","garden","cemetery","drag_lift","tree"]]]],[">",["get","rank_new"],13],["<=",["get","rank_new"],19],["!",["in",["get","category"],["literal",["peak","shop"]]]]],"minzoom":10,"maxzoom":22,"layout":{"symbol-sort-key":["get","rank_new"],"text-anchor":"top","text-justify":"center","text-field":["case",["!",["has","is_nonlatin"]],["get","name"],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]]]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Semibold"]],["literal",["Noto Sans Regular"]]],"text-offset":["interpolate",["linear"],["zoom"],8,["literal",[0,0.5]],15,["literal",[0,0.8]]],"text-padding":["interpolate",["linear"],["zoom"],1,20,18,16],"text-pitch-alignment":"viewport","text-size":["interpolate",["linear"],["zoom"],1,["interpolate",["linear"],["get","rank_new"],1,4.89,25,2.15],18,["interpolate",["linear"],["get","rank_new"],1,23.75,25,10.45]],"icon-image":["concat","sdf:",["get","type"]],"icon-padding":["interpolate",["linear"],["zoom"],1,20,18,16],"icon-size":["interpolate",["linear"],["zoom"],7,["interpolate",["linear"],["get","rank_new"],1,0.42,25,0.28],18,["interpolate",["linear"],["get","rank_new"],1,1.31,25,0.87]],"visibility":"visible"},"paint":{"text-color":["match",["get","category"],"religion","hsla(315, 10%, 60%, 1)","food","hsla(315, 20%, 40%, 1)","shop","hsla(315, 10%, 50%, 1)","education","hsla(315, 0%, 60%, 1)","sport","hsla(315, 10%, 50%, 1)","traffic","hsla(315, 10%, 60%, 1)","attraction","hsla(315, 20%, 50%, 1)","health","hsla(315, 20%, 60%, 1)","public","hsla(315, 10%, 60%, 1)","water","hsla(315, 20%, 50%, 1)","hsla(315, 0%, 40%, 1)"],"text-halo-color":["match",["get","category"],"religion","hsla(315, 10%, 100%, 0.8)","food","hsla(315, 20%, 100%, 0.8)","shop","hsla(315, 10%, 100%, 0.8)","education","hsla(315, 0%, 100%, 0.8)","sport","hsla(315, 10%, 100%, 0.8)","traffic","hsla(315, 10%, 100%, 0.8)","attraction","hsla(315, 20%, 100%, 0.8)","health","hsla(315, 20%, 100%, 0.8)","public","hsla(315, 10%, 100%, 0.8)","water","hsla(315, 20%, 100%, 0.8)","hsla(315, 0%, 100%, 0.8)"],"text-halo-width":0.5,"text-halo-blur":0.5,"icon-color":["match",["get","category"],"religion","hsla(315, 10%, 60%, 1)","food","hsla(315, 20%, 40%, 1)","shop","hsla(315, 10%, 50%, 1)","education","hsla(315, 0%, 60%, 1)","sport","hsla(315, 10%, 50%, 1)","traffic","hsla(315, 10%, 60%, 1)","attraction","hsla(315, 20%, 50%, 1)","health","hsla(315, 20%, 60%, 1)","public","hsla(315, 10%, 60%, 1)","water","hsla(315, 20%, 50%, 1)","hsla(315, 0%, 40%, 1)"],"icon-halo-color":["match",["get","category"],"religion","hsla(315, 10%, 100%, 1)","food","hsla(315, 20%, 100%, 1)","shop","hsla(315, 10%, 100%, 1)","education","hsla(315, 0%, 100%, 1)","sport","hsla(315, 10%, 100%, 1)","traffic","hsla(315, 10%, 100%, 1)","attraction","hsla(315, 20%, 100%, 1)","health","hsla(315, 20%, 100%, 1)","public","hsla(315, 10%, 100%, 1)","water","hsla(315, 20%, 100%, 1)","hsla(315, 0%, 100%, 1)"],"icon-halo-width":1.5,"icon-halo-blur":1.5}},{"id":"water_label_line_rank_3","source":"mtk","source-layer":"water_label","type":"symbol","filter":["all",["==",["geometry-type"],"LineString"],[">",["get","rank"],13],["<=",["get","rank"],17],["!=",["get","crossing"],"tunnel"]],"minzoom":9,"maxzoom":22,"layout":{"symbol-sort-key":["get","rank"],"symbol-avoid-edges":false,"symbol-placement":"line","symbol-spacing":["interpolate",["exponential",0.9],["zoom"],1,73,18,1226],"text-field":["case",["!",["has","is_nonlatin"]],["get","name"],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]]]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Italic"]],["literal",["Noto Sans Italic"]]],"text-letter-spacing":["interpolate",["linear"],["zoom"],1,0,18,["interpolate",["exponential",0.95],["get","rank"],1,0.95,25,0]],"text-pitch-alignment":"viewport","text-size":["interpolate",["exponential",0.97],["zoom"],1,["interpolate",["linear"],["get","rank"],1,5.38,17,2.69],14,["interpolate",["linear"],["get","rank"],1,26.13,17,13.06]],"visibility":"visible"},"paint":{"text-color":"hsla(212.5, 55%, 40%, 1)","text-halo-color":"hsla(212.5, 50%, 100%, 1)","text-halo-width":1,"text-halo-blur":1}},{"id":"water_label_point_rank_3","source":"mtk","source-layer":"water_label","type":"symbol","filter":["all",["==",["geometry-type"],"Point"],[">",["get","rank"],13],["<=",["get","rank"],17]],"minzoom":9,"maxzoom":22,"layout":{"symbol-sort-key":["get","rank"],"symbol-placement":"point","text-field":["case",["!",["has","is_nonlatin"]],["get","name"],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]]]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Italic"]],["literal",["Noto Sans Italic"]]],"text-letter-spacing":["interpolate",["linear"],["zoom"],1,0,18,["interpolate",["exponential",0.95],["get","rank"],1,0.71,25,0]],"text-pitch-alignment":"viewport","text-size":["interpolate",["exponential",0.97],["zoom"],1,["interpolate",["linear"],["get","rank"],1,5.87,23,2.35],18,["interpolate",["linear"],["get","rank"],1,28.5,23,11.4]],"text-padding":["interpolate",["linear"],["zoom"],1,20,18,16],"visibility":"visible"},"paint":{"text-color":"hsla(212.5, 55%, 40%, 1)","text-halo-color":"hsla(212.5, 50%, 100%, 1)","text-halo-width":1.5,"text-halo-blur":1.5}},{"id":"poi_label_peak_rank_3","source":"mtk","source-layer":"poi_label","type":"symbol","minzoom":10,"maxzoom":22,"filter":["all",["in",["get","type"],["literal",["peak","mountain_pass"]]],[">",["get","rank_new"],13],["<=",["get","rank_new"],17]],"layout":{"symbol-sort-key":["get","rank_new"],"text-anchor":"center","text-justify":"left","text-field":["case",["!",["has","is_nonlatin"]],["concat",["get","name"],"\n",["get","ele"]],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]],"\n",["get","ele"]]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Italic"]],["literal",["Noto Sans Italic"]]],"text-padding":["interpolate",["linear"],["zoom"],1,20,18,16],"text-pitch-alignment":"viewport","text-size":["interpolate",["linear"],["zoom"],1,["interpolate",["linear"],["get","rank_new"],1,5.38,25,0.98],18,["interpolate",["linear"],["get","rank_new"],1,31.61,25,5.75]],"visibility":"visible"},"paint":{"text-color":"hsla(315, 0%, 20%, 1)","text-halo-color":"hsla(315, 0%, 90%, 0.8)","text-halo-width":1,"text-halo-blur":1}},{"id":"place_label_line_rank_3","source":"mtk","source-layer":"place_label","type":"symbol","minzoom":10,"maxzoom":22,"filter":["all",["==",["geometry-type"],"LineString"],[">",["get","rank"],13],["<=",["get","rank"],17],["!",["in",["get","category"],["literal",["winter_sports","protected_area","military"]]]]],"layout":{"visibility":"visible","symbol-placement":"line-center","symbol-sort-key":["get","rank"],"symbol-spacing":["interpolate",["exponential",0.9],["zoom"],1,73,18,1226],"text-field":["case",["!",["has","is_nonlatin"]],["get","name"],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]]]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Italic"]],["literal",["Noto Sans Italic"]]],"text-pitch-alignment":"viewport","text-size":["interpolate",["exponential",0.97],["zoom"],1,["interpolate",["linear"],["get","rank"],1,5.38,17,2.69],14,["interpolate",["linear"],["get","rank"],1,26.13,17,13.06]],"text-letter-spacing":["interpolate",["linear"],["zoom"],1,0,18,["interpolate",["exponential",0.95],["get","rank"],1,0.95,25,0]]},"paint":{"text-color":["interpolate",["linear"],["zoom"],1,["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 20%, 1)",25,"hsla(0, 0%, 40%, 1)"],13,["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 0%, 1)",25,"hsla(0, 0%, 20%, 1)"]],"text-halo-color":["interpolate",["linear"],["zoom"],1,"hsla(0, 0%, 100%, 0.8)",13,["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 85%, 0.8)",25,"hsla(0, 0%, 100%, 0.8)"]],"text-halo-width":1,"text-halo-blur":1}},{"id":"place_label_rank_3","source":"mtk","source-layer":"place_label","type":"symbol","minzoom":6,"maxzoom":22,"filter":["all",["==",["geometry-type"],"Point"],[">",["get","rank"],13],["<=",["get","rank"],17],["!",["in",["get","category"],["literal",["winter_sports","protected_area","military"]]]]],"layout":{"visibility":"visible","symbol-sort-key":["get","rank"],"text-field":["case",["!",["has","is_nonlatin"]],["get","name"],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]]]],"text-font":["case",["!",["has","is_nonlatin"]],["match",["get","category"],"country",["literal",["Proza Libre Regular"]],"capital",["literal",["Proza Libre Bold"]],"big_place",["literal",["Proza Libre Bold"]],"small_place",["literal",["Proza Libre Medium"]],"other",["literal",["Proza Libre Italic"]],"park",["literal",["Proza Libre Italic"]],["literal",["Proza Libre Bold Italic"]]],["match",["get","category"],"country",["literal",["Noto Sans Regular"]],"capital",["literal",["Noto Sans Bold"]],"big_place",["literal",["Noto Sans Bold"]],"small_place",["literal",["Noto Sans Regular"]],"other",["literal",["Noto Sans Italic"]],"park",["literal",["Noto Sans Italic"]],["literal",["Noto Sans Bold Italic"]]]],"text-pitch-alignment":"viewport","text-transform":["case",["in",["get","category"],["literal",["country","capital"]]],"uppercase","none"],"text-size":["interpolate",["exponential",0.97],["zoom"],1,["interpolate",["linear"],["get","rank"],1,6.36,23,2.35],18,["interpolate",["linear"],["get","rank"],1,30.88,23,11.4]],"text-padding":["interpolate",["linear"],["zoom"],1,20,18,16],"text-letter-spacing":["interpolate",["linear"],["zoom"],1,0,18,["match",["get","category"],["country","other"],["interpolate",["exponential",0.95],["get","rank"],1,0.71,25,0],0]],"text-offset":["literal",[0,-0.2]]},"paint":{"text-color":["interpolate",["linear"],["zoom"],1,["match",["get","category"],["national_park","protected_area","park"],"hsla(-180, 35%, 35%, 1)","military","hsla(45, 25%, 60%, 1)","aboriginal_lands","hsla(95.5, 55%, 43%, 1)",["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 20%, 1)",25,"hsla(0, 0%, 40%, 1)"]],13,["match",["get","category"],["national_park","protected_area","park"],"hsla(-180, 35%, 35%, 1)","military","hsla(45, 25%, 60%, 1)","aboriginal_lands","hsla(95.5, 55%, 43%, 1)",["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 0%, 1)",25,"hsla(0, 0%, 20%, 1)"]]],"text-halo-color":["interpolate",["linear"],["zoom"],1,"hsla(0, 0%, 100%, 0.8)",13,["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 85%, 0.8)",25,"hsla(0, 0%, 100%, 0.8)"]],"text-halo-width":1,"text-halo-blur":1}},{"id":"poi_label_symbol_rank_2","source":"mtk","source-layer":"poi_label","type":"symbol","filter":["all",["!",["in",["get","type"],["literal",["peak","mountain_pass","entrance","park","garden","cemetery","drag_lift","tree"]]]],[">",["get","rank_new"],10],["<=",["get","rank_new"],13],["!",["in",["get","category"],["literal",["peak","shop"]]]]],"minzoom":7,"maxzoom":22,"layout":{"symbol-sort-key":["get","rank_new"],"text-anchor":"top","text-justify":"center","text-field":["case",["!",["has","is_nonlatin"]],["get","name"],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]]]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Semibold"]],["literal",["Noto Sans Regular"]]],"text-offset":["interpolate",["linear"],["zoom"],8,["literal",[0,0.5]],15,["literal",[0,0.8]]],"text-padding":["interpolate",["linear"],["zoom"],1,20,18,16],"text-pitch-alignment":"viewport","text-size":["interpolate",["linear"],["zoom"],1,["interpolate",["linear"],["get","rank_new"],1,4.89,25,2.15],18,["interpolate",["linear"],["get","rank_new"],1,23.75,25,10.45]],"icon-image":["concat","sdf:",["get","type"]],"icon-padding":["interpolate",["linear"],["zoom"],1,20,18,16],"icon-size":["interpolate",["linear"],["zoom"],7,["interpolate",["linear"],["get","rank_new"],1,0.42,25,0.28],18,["interpolate",["linear"],["get","rank_new"],1,1.31,25,0.87]],"visibility":"visible"},"paint":{"text-color":["match",["get","category"],"religion","hsla(315, 20%, 60%, 1)","food","hsla(315, 20%, 40%, 1)","shop","hsla(315, 10%, 50%, 1)","education","hsla(315, 10%, 60%, 1)","sport","hsla(315, 20%, 50%, 1)","traffic","hsla(315, 20%, 60%, 1)","attraction","hsla(315, 20%, 50%, 1)","health","hsla(315, 20%, 60%, 1)","public","hsla(315, 20%, 60%, 1)","water","hsla(315, 20%, 50%, 1)","hsla(315, 0%, 40%, 1)"],"text-halo-color":["match",["get","category"],"religion","hsla(315, 20%, 100%, 0.8)","food","hsla(315, 20%, 100%, 0.8)","shop","hsla(315, 10%, 100%, 0.8)","education","hsla(315, 10%, 100%, 0.8)","sport","hsla(315, 20%, 100%, 0.8)","traffic","hsla(315, 20%, 100%, 0.8)","attraction","hsla(315, 20%, 100%, 0.8)","health","hsla(315, 20%, 100%, 0.8)","public","hsla(315, 20%, 100%, 0.8)","water","hsla(315, 20%, 100%, 0.8)","hsla(315, 0%, 100%, 0.8)"],"text-halo-width":0.5,"text-halo-blur":0.5,"icon-color":["match",["get","category"],"religion","hsla(315, 20%, 60%, 1)","food","hsla(315, 20%, 40%, 1)","shop","hsla(315, 10%, 50%, 1)","education","hsla(315, 10%, 60%, 1)","sport","hsla(315, 20%, 50%, 1)","traffic","hsla(315, 20%, 60%, 1)","attraction","hsla(315, 20%, 50%, 1)","health","hsla(315, 20%, 60%, 1)","public","hsla(315, 20%, 60%, 1)","water","hsla(315, 20%, 50%, 1)","hsla(315, 0%, 40%, 1)"],"icon-halo-color":["match",["get","category"],"religion","hsla(315, 20%, 100%, 1)","food","hsla(315, 20%, 100%, 1)","shop","hsla(315, 10%, 100%, 1)","education","hsla(315, 10%, 100%, 1)","sport","hsla(315, 20%, 100%, 1)","traffic","hsla(315, 20%, 100%, 1)","attraction","hsla(315, 20%, 100%, 1)","health","hsla(315, 20%, 100%, 1)","public","hsla(315, 20%, 100%, 1)","water","hsla(315, 20%, 100%, 1)","hsla(315, 0%, 100%, 1)"],"icon-halo-width":1.5,"icon-halo-blur":1.5}},{"id":"water_label_line_rank_2","source":"mtk","source-layer":"water_label","type":"symbol","filter":["all",["==",["geometry-type"],"LineString"],[">",["get","rank"],10],["<=",["get","rank"],13],["!=",["get","crossing"],"tunnel"]],"minzoom":7,"maxzoom":22,"layout":{"symbol-sort-key":["get","rank"],"symbol-avoid-edges":false,"symbol-placement":"line","symbol-spacing":["interpolate",["exponential",0.9],["zoom"],1,73,18,1226],"text-field":["case",["!",["has","is_nonlatin"]],["get","name"],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]]]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Italic"]],["literal",["Noto Sans Italic"]]],"text-letter-spacing":["interpolate",["linear"],["zoom"],1,0,18,["interpolate",["exponential",0.95],["get","rank"],1,0.95,25,0]],"text-pitch-alignment":"viewport","text-size":["interpolate",["exponential",0.97],["zoom"],1,["interpolate",["linear"],["get","rank"],1,5.38,17,2.69],14,["interpolate",["linear"],["get","rank"],1,26.13,17,13.06]],"visibility":"visible"},"paint":{"text-color":"hsla(212.5, 55%, 40%, 1)","text-halo-color":"hsla(212.5, 50%, 100%, 1)","text-halo-width":1,"text-halo-blur":1}},{"id":"water_label_point_rank_2","source":"mtk","source-layer":"water_label","type":"symbol","filter":["all",["==",["geometry-type"],"Point"],[">",["get","rank"],10],["<=",["get","rank"],13]],"minzoom":6,"maxzoom":22,"layout":{"symbol-sort-key":["get","rank"],"symbol-placement":"point","text-field":["case",["!",["has","is_nonlatin"]],["get","name"],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]]]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Italic"]],["literal",["Noto Sans Italic"]]],"text-letter-spacing":["interpolate",["linear"],["zoom"],1,0,18,["interpolate",["exponential",0.95],["get","rank"],1,0.71,25,0]],"text-pitch-alignment":"viewport","text-size":["interpolate",["exponential",0.97],["zoom"],1,["interpolate",["linear"],["get","rank"],1,5.87,23,2.35],18,["interpolate",["linear"],["get","rank"],1,28.5,23,11.4]],"text-padding":["interpolate",["linear"],["zoom"],1,20,18,16],"visibility":"visible"},"paint":{"text-color":"hsla(212.5, 55%, 40%, 1)","text-halo-color":"hsla(212.5, 50%, 100%, 1)","text-halo-width":1.5,"text-halo-blur":1.5}},{"id":"poi_label_peak_rank_2","source":"mtk","source-layer":"poi_label","type":"symbol","minzoom":7,"maxzoom":22,"filter":["all",["in",["get","type"],["literal",["peak","mountain_pass"]]],[">",["get","rank_new"],10],["<=",["get","rank_new"],13]],"layout":{"symbol-sort-key":["get","rank_new"],"text-anchor":"center","text-justify":"left","text-field":["case",["!",["has","is_nonlatin"]],["concat",["get","name"],"\n",["get","ele"]],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]],"\n",["get","ele"]]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Italic"]],["literal",["Noto Sans Italic"]]],"text-padding":["interpolate",["linear"],["zoom"],1,20,18,16],"text-pitch-alignment":"viewport","text-size":["interpolate",["linear"],["zoom"],1,["interpolate",["linear"],["get","rank_new"],1,5.38,25,0.98],18,["interpolate",["linear"],["get","rank_new"],1,31.61,25,5.75]],"visibility":"visible"},"paint":{"text-color":"hsla(315, 0%, 20%, 1)","text-halo-color":"hsla(315, 0%, 90%, 0.8)","text-halo-width":1,"text-halo-blur":1}},{"id":"place_label_line_rank_2","source":"mtk","source-layer":"place_label","type":"symbol","minzoom":7,"maxzoom":22,"filter":["all",["==",["geometry-type"],"LineString"],[">",["get","rank"],10],["<=",["get","rank"],13],["!",["in",["get","category"],["literal",["winter_sports","protected_area","military"]]]]],"layout":{"visibility":"visible","symbol-placement":"line-center","symbol-sort-key":["get","rank"],"symbol-spacing":["interpolate",["exponential",0.9],["zoom"],1,73,18,1226],"text-field":["case",["!",["has","is_nonlatin"]],["get","name"],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]]]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Italic"]],["literal",["Noto Sans Italic"]]],"text-pitch-alignment":"viewport","text-size":["interpolate",["exponential",0.97],["zoom"],1,["interpolate",["linear"],["get","rank"],1,5.38,17,2.69],14,["interpolate",["linear"],["get","rank"],1,26.13,17,13.06]],"text-letter-spacing":["interpolate",["linear"],["zoom"],1,0,18,["interpolate",["exponential",0.95],["get","rank"],1,0.95,25,0]]},"paint":{"text-color":["interpolate",["linear"],["zoom"],1,["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 20%, 1)",25,"hsla(0, 0%, 40%, 1)"],13,["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 0%, 1)",25,"hsla(0, 0%, 20%, 1)"]],"text-halo-color":["interpolate",["linear"],["zoom"],1,"hsla(0, 0%, 100%, 0.8)",13,["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 85%, 0.8)",25,"hsla(0, 0%, 100%, 0.8)"]],"text-halo-width":1,"text-halo-blur":1}},{"id":"place_label_rank_2","source":"mtk","source-layer":"place_label","type":"symbol","minzoom":6,"maxzoom":22,"filter":["all",["==",["geometry-type"],"Point"],[">",["get","rank"],10],["<=",["get","rank"],13],["!",["in",["get","category"],["literal",["winter_sports","protected_area","military"]]]]],"layout":{"visibility":"visible","symbol-sort-key":["get","rank"],"text-field":["case",["!",["has","is_nonlatin"]],["get","name"],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]]]],"text-font":["case",["!",["has","is_nonlatin"]],["match",["get","category"],"country",["literal",["Proza Libre Regular"]],"capital",["literal",["Proza Libre Bold"]],"big_place",["literal",["Proza Libre Bold"]],"small_place",["literal",["Proza Libre Medium"]],"other",["literal",["Proza Libre Italic"]],"park",["literal",["Proza Libre Italic"]],["literal",["Proza Libre Bold Italic"]]],["match",["get","category"],"country",["literal",["Noto Sans Regular"]],"capital",["literal",["Noto Sans Bold"]],"big_place",["literal",["Noto Sans Bold"]],"small_place",["literal",["Noto Sans Regular"]],"other",["literal",["Noto Sans Italic"]],"park",["literal",["Noto Sans Italic"]],["literal",["Noto Sans Bold Italic"]]]],"text-pitch-alignment":"viewport","text-transform":["case",["in",["get","category"],["literal",["country","capital"]]],"uppercase","none"],"text-size":["interpolate",["exponential",0.97],["zoom"],1,["interpolate",["linear"],["get","rank"],1,6.36,23,2.35],18,["interpolate",["linear"],["get","rank"],1,30.88,23,11.4]],"text-padding":["interpolate",["linear"],["zoom"],1,20,18,16],"text-letter-spacing":["interpolate",["linear"],["zoom"],1,0,18,["match",["get","category"],["country","other"],["interpolate",["exponential",0.95],["get","rank"],1,0.71,25,0],0]],"text-offset":["literal",[0,-0.2]]},"paint":{"text-color":["interpolate",["linear"],["zoom"],1,["match",["get","category"],["national_park","protected_area","park"],"hsla(-180, 35%, 35%, 1)","military","hsla(45, 25%, 60%, 1)","aboriginal_lands","hsla(95.5, 55%, 43%, 1)",["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 20%, 1)",25,"hsla(0, 0%, 40%, 1)"]],13,["match",["get","category"],["national_park","protected_area","park"],"hsla(-180, 35%, 35%, 1)","military","hsla(45, 25%, 60%, 1)","aboriginal_lands","hsla(95.5, 55%, 43%, 1)",["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 0%, 1)",25,"hsla(0, 0%, 20%, 1)"]]],"text-halo-color":["interpolate",["linear"],["zoom"],1,"hsla(0, 0%, 100%, 0.8)",13,["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 85%, 0.8)",25,"hsla(0, 0%, 100%, 0.8)"]],"text-halo-width":1,"text-halo-blur":1}},{"id":"water_label_line_rank_1","source":"mtk","source-layer":"water_label","type":"symbol","filter":["all",["==",["geometry-type"],"LineString"],["<=",["get","rank"],10],["!=",["get","crossing"],"tunnel"]],"minzoom":3,"maxzoom":22,"layout":{"symbol-sort-key":["get","rank"],"symbol-avoid-edges":false,"symbol-placement":"line","symbol-spacing":["interpolate",["exponential",0.9],["zoom"],1,73,18,1226],"text-field":["case",["!",["has","is_nonlatin"]],["get","name"],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]]]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Italic"]],["literal",["Noto Sans Italic"]]],"text-letter-spacing":["interpolate",["linear"],["zoom"],1,0,18,["interpolate",["exponential",0.95],["get","rank"],1,0.95,25,0]],"text-pitch-alignment":"viewport","text-size":["interpolate",["exponential",0.97],["zoom"],1,["interpolate",["linear"],["get","rank"],1,5.38,17,2.69],14,["interpolate",["linear"],["get","rank"],1,26.13,17,13.06]],"visibility":"visible"},"paint":{"text-color":"hsla(212.5, 55%, 40%, 1)","text-halo-color":"hsla(212.5, 50%, 100%, 1)","text-halo-width":1,"text-halo-blur":1}},{"id":"water_label_point_rank_1","source":"mtk","source-layer":"water_label","type":"symbol","filter":["all",["==",["geometry-type"],"Point"],["<=",["get","rank"],10]],"minzoom":1,"maxzoom":22,"layout":{"symbol-sort-key":["get","rank"],"symbol-placement":"point","text-field":["case",["!",["has","is_nonlatin"]],["get","name"],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]]]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Italic"]],["literal",["Noto Sans Italic"]]],"text-letter-spacing":["interpolate",["linear"],["zoom"],1,0,18,["interpolate",["exponential",0.95],["get","rank"],1,0.71,25,0]],"text-pitch-alignment":"viewport","text-size":["interpolate",["exponential",0.97],["zoom"],1,["interpolate",["linear"],["get","rank"],1,5.87,23,2.35],18,["interpolate",["linear"],["get","rank"],1,28.5,23,11.4]],"text-padding":["interpolate",["linear"],["zoom"],1,20,18,16],"visibility":"visible"},"paint":{"text-color":"hsla(212.5, 55%, 40%, 1)","text-halo-color":"hsla(212.5, 50%, 100%, 1)","text-halo-width":1.5,"text-halo-blur":1.5}},{"id":"poi_label_peak_rank_1","source":"mtk","source-layer":"poi_label","type":"symbol","minzoom":7,"maxzoom":22,"filter":["all",["in",["get","type"],["literal",["peak","mountain_pass"]]],["<=",["get","rank_new"],10]],"layout":{"symbol-sort-key":["get","rank_new"],"text-anchor":"center","text-justify":"left","text-field":["case",["!",["has","is_nonlatin"]],["concat",["get","name"],"\n",["get","ele"]],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]],"\n",["get","ele"]]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Italic"]],["literal",["Noto Sans Italic"]]],"text-padding":["interpolate",["linear"],["zoom"],1,20,18,16],"text-pitch-alignment":"viewport","text-size":["interpolate",["linear"],["zoom"],1,["interpolate",["linear"],["get","rank_new"],1,5.38,25,0.98],18,["interpolate",["linear"],["get","rank_new"],1,31.61,25,5.75]],"visibility":"visible"},"paint":{"text-color":"hsla(315, 0%, 20%, 1)","text-halo-color":"hsla(315, 0%, 90%, 0.8)","text-halo-width":1,"text-halo-blur":1}},{"id":"place_label_line_rank_1","source":"mtk","source-layer":"place_label","type":"symbol","minzoom":3,"maxzoom":22,"filter":["all",["==",["geometry-type"],"LineString"],["<=",["get","rank"],10],["!",["in",["get","category"],["literal",["winter_sports","protected_area","military"]]]]],"layout":{"visibility":"visible","symbol-placement":"line-center","symbol-sort-key":["get","rank"],"symbol-spacing":["interpolate",["exponential",0.9],["zoom"],1,73,18,1226],"text-field":["case",["!",["has","is_nonlatin"]],["get","name"],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]]]],"text-font":["case",["!",["has","is_nonlatin"]],["literal",["Proza Libre Italic"]],["literal",["Noto Sans Italic"]]],"text-pitch-alignment":"viewport","text-size":["interpolate",["exponential",0.97],["zoom"],1,["interpolate",["linear"],["get","rank"],1,5.38,17,2.69],14,["interpolate",["linear"],["get","rank"],1,26.13,17,13.06]],"text-letter-spacing":["interpolate",["linear"],["zoom"],1,0,18,["interpolate",["exponential",0.95],["get","rank"],1,0.95,25,0]]},"paint":{"text-color":["interpolate",["linear"],["zoom"],1,["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 20%, 1)",25,"hsla(0, 0%, 40%, 1)"],13,["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 0%, 1)",25,"hsla(0, 0%, 20%, 1)"]],"text-halo-color":["interpolate",["linear"],["zoom"],1,"hsla(0, 0%, 100%, 0.8)",13,["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 85%, 0.8)",25,"hsla(0, 0%, 100%, 0.8)"]],"text-halo-width":1,"text-halo-blur":1}},{"id":"place_label_rank_1","source":"mtk","source-layer":"place_label","type":"symbol","minzoom":1,"maxzoom":22,"filter":["all",["==",["geometry-type"],"Point"],["<=",["get","rank"],10],["!",["in",["get","category"],["literal",["winter_sports","protected_area","military"]]]]],"layout":{"visibility":"visible","symbol-sort-key":["get","rank"],"text-field":["case",["!",["has","is_nonlatin"]],["get","name"],["concat",["get","name"],"\n",["coalesce",["get","name_en"],["get","name_fr"],["get","name_es"],["get","name_de"]]]],"text-font":["case",["!",["has","is_nonlatin"]],["match",["get","category"],"country",["literal",["Proza Libre Regular"]],"capital",["literal",["Proza Libre Bold"]],"big_place",["literal",["Proza Libre Bold"]],"small_place",["literal",["Proza Libre Medium"]],"other",["literal",["Proza Libre Italic"]],"park",["literal",["Proza Libre Italic"]],["literal",["Proza Libre Bold Italic"]]],["match",["get","category"],"country",["literal",["Noto Sans Regular"]],"capital",["literal",["Noto Sans Bold"]],"big_place",["literal",["Noto Sans Bold"]],"small_place",["literal",["Noto Sans Regular"]],"other",["literal",["Noto Sans Italic"]],"park",["literal",["Noto Sans Italic"]],["literal",["Noto Sans Bold Italic"]]]],"text-pitch-alignment":"viewport","text-transform":["case",["in",["get","category"],["literal",["country","capital"]]],"uppercase","none"],"text-size":["interpolate",["exponential",0.97],["zoom"],1,["interpolate",["linear"],["get","rank"],1,6.36,23,2.35],18,["interpolate",["linear"],["get","rank"],1,30.88,23,11.4]],"text-padding":["interpolate",["linear"],["zoom"],1,20,18,16],"text-letter-spacing":["interpolate",["linear"],["zoom"],1,0,18,["match",["get","category"],["country","other"],["interpolate",["exponential",0.95],["get","rank"],1,0.71,25,0],0]],"text-offset":["literal",[0,-0.2]]},"paint":{"text-color":["interpolate",["linear"],["zoom"],1,["match",["get","category"],["national_park","protected_area","park"],"hsla(-180, 35%, 35%, 1)","military","hsla(45, 25%, 60%, 1)","aboriginal_lands","hsla(95.5, 55%, 43%, 1)",["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 20%, 1)",25,"hsla(0, 0%, 40%, 1)"]],13,["match",["get","category"],["national_park","protected_area","park"],"hsla(-180, 35%, 35%, 1)","military","hsla(45, 25%, 60%, 1)","aboriginal_lands","hsla(95.5, 55%, 43%, 1)",["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 0%, 1)",25,"hsla(0, 0%, 20%, 1)"]]],"text-halo-color":["interpolate",["linear"],["zoom"],1,"hsla(0, 0%, 100%, 0.8)",13,["interpolate",["linear"],["get","rank"],1,"hsla(0, 0%, 85%, 0.8)",25,"hsla(0, 0%, 100%, 0.8)"]],"text-halo-width":1,"text-halo-blur":1}}]', FALSE, '', TRUE, TRUE);

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
