--
-- PostgreSQL database dump
--

-- Dumped from database version 9.1.4
-- Dumped by pg_dump version 9.1.4
-- Started on 2013-06-25 15:32:29

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = app_metadata, pg_catalog;

--- TOC entry 3497 (class 0 OID 1298165)
--- Dependencies: 207
--- Data for Name: app_config; Type: TABLE DATA; Schema: app_metadata; Owner: postgres
 
COPY app_config (name, defaultvalue, datatype, notes, isprivate) FROM stdin;
defaultFeatureLayer	{\n        style:{\n            default:{\n                fillColor: "#008040",\n                fillOpacity: 0.5,\n                strokeColor: "#ee9900",\n                strokeOpacity: .7,\n                strokeWidth: 1,\n                pointRadius: 8\n            },\n            select: {\n                fillColor: "#66ccff",\n                strokeColor: "#3399ff",\n                graphicZIndex: 2\n            }\n        }\n    }	json	defines the initial state of the map	f
mapConfig	{\n        maxExtent: new OpenLayers.Bounds(-200000, -200000, 200000, 200000),\n        center: new OpenLayers.LonLat(-224149.03751366, 6978966.6705368),\n        zoom: 6,\n        numZoomLevels: 19,\n        minZoomLevel: 1,\n        fallThrough: false,\n        controls: [new OpenLayers.Control.Navigation(), new OpenLayers.Control.Zoom()],\n        displayProjection: new OpenLayers.Projection("EPSG:4326"),\n        theme: null\n    }	json	defines the initial state of the map	f
default_language	en-us	text	the default language to use for the application ui	f
\.


---
--- TOC entry 3504 (class 0 OID 1298214)
--- Dependencies: 217
--- Data for Name: reports; Type: TABLE DATA; Schema: app_metadata; Owner: postgres
---

COPY reports (reportid, name_i18n_key, widgetname) FROM stdin;
1	report_name	Arches.reports.Default
\.



--
-- TOC entry 3500 (class 0 OID 1298185)
-- Dependencies: 211
-- Data for Name: i18n; Type: TABLE DATA; Schema: app_metadata; Owner: postgres
--

COPY i18n (key, value, languageid, widgetname) FROM stdin;
report_name	Default	en-us	Arches.reports.Default
currentZoomLevelLabel	Current Zoom Level:	en-us	Arches.widgets.MapPanel
cursorPositionLabel	Cursor Position:	en-us	Arches.widgets.MapPanel
advancedSearchLink	Advanced Search	en-us	Arches.widgets.AppHeader
simpleSearchLink	Search	en-us	Arches.widgets.AppHeader
entitySearchMask	Find an Entity	en-us	Arches.widgets.AppHeader
usernameDisplayPrefix	Welcome	en-us	Arches.widgets.AppHeader
subtitle	National Heritage and Documentation System	en-us	Arches.widgets.AppHeader
administrationLink	Administration	en-us	Arches.widgets.AppHeader
tutorialsLink	Tutorials	en-us	Arches.widgets.AppHeader
title	Heritage Map	en-us	Arches.widgets.AppHeader
selectLayersMapsButtonText	Layers/Maps	en-us	Arches.widgets.AppPanel
layerListTitle	Map Layers on and off	en-us	Arches.widgets.AppPanel
layerListSubTitle	Turn visibility of layers on and off	en-us	Arches.widgets.AppPanel
layerListButtonText	Map</br>Layers	en-us	Arches.widgets.AppPanel
newEntityButtonText	Add New Entity	en-us	Arches.widgets.AppPanel
searchResultsTitle	Search Results	en-us	Arches.widgets.LegendPanel
authorshipTitle	Authorship	en-us	Arches.widgets.LegendPanel
mapDetailsTitle	Map Details	en-us	Arches.widgets.LegendPanel
backButtonText	Back	en-us	Arches.widgets.LayerList
hideAllButtonText	Hide All	en-us	Arches.widgets.LayerList
showAllButtonText	Show All	en-us	Arches.widgets.LayerList
title	Legend	en-us	Arches.widgets.LayerList
underConstructionMessage	This feature is coming soon!	en-us	Arches.app
underConstructionHeader	Under Construction...	en-us	Arches.app
loginMask	Signing In...	en-us	Arches.app
appInitMask	Initializing...	en-us	Arches.app
Basemaps	Basemaps	en-us	Arches.widgets.LayerLibrary
Assets	Resources	en-us	Arches.widgets.LayerLibrary
Google_Streets	Google Streets	en-us	Arches.widgets.LayerLibrary
Google_Hybrid	Google Hybrid	en-us	Arches.widgets.LayerLibrary
Google_Satellite	Google Satellite	en-us	Arches.widgets.LayerLibrary
Precipitation	Precipitation	en-us	Arches.widgets.LayerLibrary
External_Services	External Services	en-us	Arches.widgets.LayerLibrary
\.


--
-- TOC entry 3503 (class 0 OID 1298202)
-- Dependencies: 215
-- Data for Name: maplayers; Type: TABLE DATA; Schema: app_metadata; Owner: postgres
--

COPY maplayers (id, active, on_map, selectable, basemap, name_i18n_key, icon, symbology, thumbnail, description_i18n_key, layergroup_i18n_key, layer, sortorder) FROM stdin;
1	f	f	f	t	Google_Streets	GoogleStreets	\N	GoogleStreets	\N	Basemaps	return new OpenLayers.Layer.Google("Google Streets", { numZoomLevels: Arches.config.App.mapConfig.numZoomLevels, sphericalMercator: true, MIN_ZOOM_LEVEL: Arches.config.App.mapConfig.minZoomLevel, projection: new OpenLayers.Projection("EPSG:900913") });	\N
2	t	t	f	t	Google_Hybrid	GoogleHybrid	\N	GoogleHybrid	\N	Basemaps	return new OpenLayers.Layer.Google("Google Hybrid",{ type: google.maps.MapTypeId.HYBRID, numZoomLevels: Arches.config.App.mapConfig.numZoomLevels, sphericalMercator: true, MIN_ZOOM_LEVEL: Arches.config.App.mapConfig.minZoomLevel, projection: new OpenLayers.Projection("EPSG:900913") });	\N
3	f	f	f	t	Google_Satellite	GoogleSatellite	\N	GoogleSatellite	\N	Basemaps	return new OpenLayers.Layer.Google("Google Satellite",{ type: google.maps.MapTypeId.SATELLITE, numZoomLevels: Arches.config.App.mapConfig.numZoomLevels, sphericalMercator: true, MIN_ZOOM_LEVEL: Arches.config.App.mapConfig.minZoomLevel, projection: new OpenLayers.Projection("EPSG:900913") });	\N
4	f	f	f	f	Precipitation	\N	\N	\N	\N	External_Services	return new OpenLayers.Layer.XYZ( "precipitation", "http://${s}.tile.openweathermap.org/map/precipitation/${z}/${x}/${y}.png", { isBaseLayer: false, opacity: 0.7, sphericalMercator: true } );	\N
\.

SELECT pg_catalog.setval('maplayers_id_seq', 5, true);