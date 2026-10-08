import { onUnmounted } from "vue";

import {
    COORDINATE_PREVIEW_SOURCE_ID,
    FEATURE_HIGHLIGHT_COLOR,
    VERTEX_HIGHLIGHT_SOURCE_ID,
} from "@/arches_vue_components/components/MapComponent/constants.ts";
import { geometriesToFeatureCollection } from "@/arches_vue_components/components/MapComponent/utils/feature-collection.ts";

import type { ShallowRef } from "vue";
import type { Geometry, Position } from "geojson";
import type { GeoJSONSource, Map as MaplibreMap } from "maplibre-gl";

const PREVIEW_COLOR = "#3bb2d0";
const PREVIEW_FILL_OPACITY = 0.15;
const PREVIEW_LINE_WIDTH = 2;
const PREVIEW_POINT_RADIUS = 5;
const VERTEX_HIGHLIGHT_RADIUS = 9;
const VERTEX_HIGHLIGHT_STROKE_WIDTH = 3;

const PREVIEW_FILL_LAYER_ID = `${COORDINATE_PREVIEW_SOURCE_ID}-fill`;
const PREVIEW_LINE_LAYER_ID = `${COORDINATE_PREVIEW_SOURCE_ID}-line`;
const PREVIEW_POINT_LAYER_ID = `${COORDINATE_PREVIEW_SOURCE_ID}-point`;
const VERTEX_HIGHLIGHT_LAYER_ID = `${VERTEX_HIGHLIGHT_SOURCE_ID}-point`;

const LAYER_IDS = [
    PREVIEW_FILL_LAYER_ID,
    PREVIEW_LINE_LAYER_ID,
    PREVIEW_POINT_LAYER_ID,
    VERTEX_HIGHLIGHT_LAYER_ID,
];
const SOURCE_IDS = [COORDINATE_PREVIEW_SOURCE_ID, VERTEX_HIGHLIGHT_SOURCE_ID];

export interface UseCoordinatePreviewReturn {
    showPreviewGeometry: (geometry: Geometry | null) => void;
    showVertexHighlight: (position: Position | null) => void;
}

export function useCoordinatePreview(
    map: ShallowRef<MaplibreMap | null>,
): UseCoordinatePreviewReturn {
    onUnmounted(removePreviewLayers);

    function ensurePreviewLayers(): void {
        const previewMap = map.value!;
        for (const sourceId of SOURCE_IDS) {
            if (!previewMap.getSource(sourceId)) {
                previewMap.addSource(sourceId, {
                    type: "geojson",
                    data: geometriesToFeatureCollection([]),
                });
            }
        }
        if (!previewMap.getLayer(PREVIEW_FILL_LAYER_ID)) {
            previewMap.addLayer({
                id: PREVIEW_FILL_LAYER_ID,
                type: "fill",
                source: COORDINATE_PREVIEW_SOURCE_ID,
                filter: ["==", ["geometry-type"], "Polygon"],
                paint: {
                    "fill-color": PREVIEW_COLOR,
                    "fill-opacity": PREVIEW_FILL_OPACITY,
                },
            });
        }
        if (!previewMap.getLayer(PREVIEW_LINE_LAYER_ID)) {
            previewMap.addLayer({
                id: PREVIEW_LINE_LAYER_ID,
                type: "line",
                source: COORDINATE_PREVIEW_SOURCE_ID,
                paint: {
                    "line-color": PREVIEW_COLOR,
                    "line-width": PREVIEW_LINE_WIDTH,
                    "line-dasharray": [2, 2],
                },
            });
        }
        if (!previewMap.getLayer(PREVIEW_POINT_LAYER_ID)) {
            previewMap.addLayer({
                id: PREVIEW_POINT_LAYER_ID,
                type: "circle",
                source: COORDINATE_PREVIEW_SOURCE_ID,
                filter: [
                    "in",
                    ["geometry-type"],
                    ["literal", ["Point", "MultiPoint"]],
                ],
                paint: {
                    "circle-radius": PREVIEW_POINT_RADIUS,
                    "circle-color": PREVIEW_COLOR,
                },
            });
        }
        if (!previewMap.getLayer(VERTEX_HIGHLIGHT_LAYER_ID)) {
            previewMap.addLayer({
                id: VERTEX_HIGHLIGHT_LAYER_ID,
                type: "circle",
                source: VERTEX_HIGHLIGHT_SOURCE_ID,
                paint: {
                    "circle-radius": VERTEX_HIGHLIGHT_RADIUS,
                    "circle-color": "rgba(0, 0, 0, 0)",
                    "circle-stroke-color": FEATURE_HIGHLIGHT_COLOR,
                    "circle-stroke-width": VERTEX_HIGHLIGHT_STROKE_WIDTH,
                },
            });
        }
    }

    function setSourceGeometries(
        sourceId: string,
        geometries: Geometry[],
    ): void {
        if (!map.value) {
            return;
        }

        ensurePreviewLayers();
        (map.value.getSource(sourceId) as GeoJSONSource).setData(
            geometriesToFeatureCollection(geometries),
        );
    }

    function showPreviewGeometry(geometry: Geometry | null): void {
        setSourceGeometries(
            COORDINATE_PREVIEW_SOURCE_ID,
            geometry ? [geometry] : [],
        );
    }

    function showVertexHighlight(position: Position | null): void {
        setSourceGeometries(
            VERTEX_HIGHLIGHT_SOURCE_ID,
            position ? [{ type: "Point", coordinates: position }] : [],
        );
    }

    function removePreviewLayers(): void {
        const previewMap = map.value;
        if (!previewMap) {
            return;
        }

        for (const layerId of LAYER_IDS) {
            if (previewMap.getLayer(layerId)) {
                previewMap.removeLayer(layerId);
            }
        }
        for (const sourceId of SOURCE_IDS) {
            if (previewMap.getSource(sourceId)) {
                previewMap.removeSource(sourceId);
            }
        }
    }

    return { showPreviewGeometry, showVertexHighlight };
}
