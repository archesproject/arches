import type { Component } from "vue";
import type { GeoJSON } from "geojson";

import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";

export interface GeometryTypeConfig {
    id: string;
    text: string;
}

export interface MapWidgetConfig {
    zoom?: number;
    pitch?: number;
    bearing?: number;
    centerX?: number;
    centerY?: number;
    maxZoom?: number;
    minZoom?: number;
    basemap?: string;
    featureColor?: string;
    featureLineWidth?: number;
    featurePointSize?: number;
    geometryTypes?: GeometryTypeConfig[];
    geocoderVisible?: boolean;
    geocodePlaceholder?: string;
    geocodeProvider?: string;
    overlayConfigs?: unknown[];
    overlayOpacity?: number;
}

export interface MapCardXNodeXWidgetData extends CardXNodeXWidgetData {
    config: CardXNodeXWidgetData["config"] & MapWidgetConfig;
}

export interface Basemap {
    id: string;
    name: string;
    value: string;
    active: boolean;
    url: string;
}

export interface RawBasemap {
    name: string;
    title: string;
    url: string;
    addtomap: boolean;
}

export interface LayerDefinition {
    id: string;
    type: string;
    source?: string;
    "source-layer"?: string;
    layout?: Record<string, unknown>;
    paint?: Record<string, unknown>;
    filter?: unknown;
    minzoom?: number;
    maxzoom?: number;
}

export interface MapLayer {
    activated?: boolean;
    addtomap: boolean;
    icon?: string;
    id: number;
    is_resource_layer?: boolean;
    isoverlay?: boolean;
    layerdefinitions: LayerDefinition[];
    maplayerid?: string;
    name: string;
    searchonly?: boolean;
    sortorder?: number;
    title?: string;
    url?: string;
    visible?: boolean;
}

export interface MapInteractionItem {
    name: string;
    header: string;
    component: Component;
    icon: string;
}

export interface ResourceDescriptor {
    displayname: string;
    displaydescription: string;
    map_popup: string;
    graph_name: string;
    permissions: { can_edit_resource_instance?: boolean };
}

export interface MapSource {
    id: number;
    name: string;
    source: {
        type: string;
        url?: string;
        data?: GeoJSON;
        tileSize?: number;
        coordinates?: [number, number];
    };
    source_json?: string;
}
