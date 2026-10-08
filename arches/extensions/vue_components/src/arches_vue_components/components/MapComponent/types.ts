import type { Component, ComputedRef, Ref, ShallowRef } from "vue";
import type { Feature, FeatureCollection, GeoJSON, Geometry } from "geojson";
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
    legend?: string | null;
    maplayerid: string;
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
    badgeCount?: (context: MapContext) => number;
    wide?: boolean;
}

export type DrawMode = "point" | "line" | "polygon";

export interface CoordinateSystem {
    name: string;
    srid: string;
    proj4: string;
    default?: boolean;
}

export type CoordinateReadoutFormat = "dd" | "dms";

export type MapScaleUnit = "metric" | "imperial";

export interface MapSettings {
    showCursorCoordinates: boolean;
    coordinateReadoutSrid: string;
    coordinateReadoutFormat: CoordinateReadoutFormat;
    showMapScale: boolean;
    mapScaleUnit: MapScaleUnit;
    showZoomLevel: boolean;
    geocoderVisible: boolean;
    geocoderPlaceholder?: string;
    showNavigationControl: boolean;
    showFullscreenControl: boolean;
    scrollZoomRequiresKey: boolean;
    allow3d: boolean;
}

export type OverlaySwatch =
    | { kind: "fill" | "line" | "point"; color: string }
    | { kind: "gradient"; colors: string[] }
    | { kind: "icon"; iconClass: string };

export interface MapContext {
    map: ShallowRef<MaplibreMap | null>;
    isLoading: Ref<boolean>;
    basemaps: Ref<Basemap[]>;
    overlays: Ref<MapLayer[]>;
    overlayOpacities: Ref<Record<string, number>>;
    settings: Ref<MapSettings>;
    coordinateSystems: Ref<CoordinateSystem[]>;
    drawnFeatures: ShallowRef<Feature[]>;
    selectedDrawnFeature: Ref<Feature | null>;
    allowedGeometryTypes: ComputedRef<string[] | null>;
    setDrawMode: (mode: DrawMode | null) => void;
    selectDrawnFeature: (feature: Feature) => void;
    deselectDrawnFeature: () => void;
    editDrawnFeature: (feature: Feature) => void;
    deleteDrawnFeature: (feature: Feature) => void;
    deleteSelectedDrawnFeature: () => void;
    deleteAllDrawnFeatures: () => void;
    setBufferForSelectedFeature: (distance: number, units: string) => void;
    setBufferForFeature: (
        feature: Feature,
        distance: number,
        units: string,
    ) => void;
    addFeatures: (features: Feature[]) => boolean;
    updateDrawnFeature: (feature: Feature) => void;
    fitToFeatures: (features: Feature[]) => void;
    moveOverlay: (overlay: MapLayer, toIndex: number) => void;
    setOverlayOpacity: (overlay: MapLayer, opacityPercent: number) => void;
    showFeatureHighlight: (geometries: Geometry[]) => void;
    clearFeatureHighlight: () => void;
}

export interface FeaturePopupProps {
    features: MapGeoJSONFeature[];
    context?: MapContext;
}

export interface ResourceDescriptorGeometry {
    geom: FeatureCollection;
    nodegroup_id: string;
    tileid: string;
    provisional: boolean;
}

export interface ResourceDescriptor {
    displayname: string;
    displaydescription: string;
    map_popup: string;
    graph_name: string;
    graph_iconclass: string | null;
    lifecycle_state: string;
    geometries: ResourceDescriptorGeometry[];
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
    settings?: Partial<MapSettings>;
}
