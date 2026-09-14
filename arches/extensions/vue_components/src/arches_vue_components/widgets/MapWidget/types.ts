import type { Component } from "vue";
import type { FeatureCollection } from "geojson";

import type { CardXNodeXWidgetData } from "@/arches_vue_components/types.ts";
import type { BaseWidgetProps } from "@/arches_vue_components/widgets/types.ts";
import type { GeoJSONFeatureCollectionAliasedNodeData } from "@/arches_vue_components/datatypes/geojson-feature-collection/types.ts";
import type { MapInteractionTool } from "@/arches_vue_components/components/MapComponent/types.ts";

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
    maxDrawnFeatures?: number;
}

export interface MapCardXNodeXWidgetData extends CardXNodeXWidgetData {
    config: CardXNodeXWidgetData["config"] & MapWidgetConfig;
}

export interface MapWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: MapCardXNodeXWidgetData;
    aliasedNodeData?: GeoJSONFeatureCollectionAliasedNodeData | null;
    value?: FeatureCollection | null;
    interactionTools?: MapInteractionTool[];
    featurePopupComponent?: Component;
}
