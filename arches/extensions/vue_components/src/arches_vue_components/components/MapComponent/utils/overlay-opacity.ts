import { DEFAULT_OVERLAY_OPACITY_PERCENT } from "@/arches_vue_components/components/MapComponent/constants.ts";

import type { Map as MaplibreMap } from "maplibre-gl";

import type {
    LayerDefinition,
    MapLayer,
} from "@/arches_vue_components/components/MapComponent/types.ts";

type PaintPropertyName = Parameters<MaplibreMap["setPaintProperty"]>[1];

const OPACITY_PAINT_PROPERTIES_BY_LAYER_TYPE: Record<
    string,
    PaintPropertyName[]
> = {
    background: ["background-opacity"],
    circle: ["circle-opacity", "circle-stroke-opacity"],
    fill: ["fill-opacity"],
    "fill-extrusion": ["fill-extrusion-opacity"],
    heatmap: ["heatmap-opacity"],
    line: ["line-opacity"],
    raster: ["raster-opacity"],
    symbol: ["icon-opacity", "text-opacity"],
};

const DEFAULT_PAINT_OPACITY = 1;

function getOpacityPaintProperties(
    layerDefinition: LayerDefinition,
): PaintPropertyName[] {
    return OPACITY_PAINT_PROPERTIES_BY_LAYER_TYPE[layerDefinition.type] ?? [];
}

export function getOverlayOpacityPercent(
    overlayOpacities: Record<string, number>,
    overlay: MapLayer,
): number {
    return (
        overlayOpacities[overlay.maplayerid] ?? DEFAULT_OVERLAY_OPACITY_PERCENT
    );
}

export function isOverlayOpacityAdjustable(
    layerDefinitions: LayerDefinition[],
): boolean {
    return layerDefinitions.every((layerDefinition) =>
        getOpacityPaintProperties(layerDefinition).every((property) => {
            const value = layerDefinition.paint?.[property];
            return value === undefined || typeof value === "number";
        }),
    );
}

export function buildScaledOpacityPaint(
    layerDefinition: LayerDefinition,
    opacityPercent: number,
): [PaintPropertyName, number][] {
    const factor = opacityPercent / 100;

    return getOpacityPaintProperties(layerDefinition).map((property) => {
        const value = layerDefinition.paint?.[property];
        const baseOpacity =
            typeof value === "number" ? value : DEFAULT_PAINT_OPACITY;
        return [property, baseOpacity * factor];
    });
}
