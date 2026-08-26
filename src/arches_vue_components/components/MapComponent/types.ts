import type { Component, ComputedRef, Ref, ShallowRef } from "vue";
import type { Feature, FeatureCollection, GeoJSON } from "geojson";
import type { Map as MaplibreMap, MapGeoJSONFeature } from "maplibre-gl";

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

export interface MapInteractionTool {
    name: string;
    header: string;
    component: Component;
    icon: string;
    props?: Record<string, unknown>;
}

export type DrawMode = "point" | "line" | "polygon";

export interface MapContext {
    map: ShallowRef<MaplibreMap | null>;
    isLoading: Ref<boolean>;
    basemaps: Ref<Basemap[]>;
    overlays: Ref<MapLayer[]>;
    drawnFeatures: ShallowRef<Feature[]>;
    selectedDrawnFeature: Ref<Feature | null>;
    allowedGeometryTypes: ComputedRef<string[] | null>;
    setDrawMode: (mode: DrawMode | null) => void;
    selectDrawnFeature: (feature: Feature) => void;
    deleteSelectedDrawnFeature: () => void;
    deleteAllDrawnFeatures: () => void;
    setBufferForSelectedFeature: (distance: number, units: string) => void;
    addFeatures: (features: Feature[]) => void;
}

export interface FeaturePopupProps {
    features: MapGeoJSONFeature[];
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

export interface MapComponentProps {
    value?: FeatureCollection | null;
    zoom?: number;
    pitch?: number;
    bearing?: number;
    centerX?: number;
    centerY?: number;
    minZoom?: number;
    maxZoom?: number;
    basemap?: string;
    allowedGeometryTypes?: string[];
    resolveOverlayLayers?: (candidateOverlayLayers: MapLayer[]) => MapLayer[];
    interactionTools?: MapInteractionTool[];
    maxFeatures?: number;
    featurePopupComponent?: Component;
}
