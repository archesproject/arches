import { computed, onUnmounted, watch } from "vue";

import { debounce } from "es-toolkit";

import {
    COORDINATE_PREVIEW_SOURCE_ID,
    POINT,
} from "@/arches_vue_components/components/MapComponent/constants.ts";
import { geometriesToFeatureCollection } from "@/arches_vue_components/components/MapComponent/utils/feature-collection.ts";

import type { ComputedRef, Ref } from "vue";
import type { Geometry, Position } from "geojson";
import type { AddLayerObject, GeoJSONSource } from "maplibre-gl";

import type { UseCoordinateEditorReturn } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/composables/useCoordinateEditor.ts";
import type { MapContext } from "@/arches_vue_components/components/MapComponent/types.ts";

const PREVIEW_DEBOUNCE_MILLISECONDS = 300;
const VERTEX_FOCUS_ZOOM = 17;
const PREVIEW_COLOR = "#3bb2d0";

const PREVIEW_LAYERS: AddLayerObject[] = [
    {
        id: `${COORDINATE_PREVIEW_SOURCE_ID}-fill`,
        type: "fill",
        source: COORDINATE_PREVIEW_SOURCE_ID,
        filter: ["==", ["geometry-type"], "Polygon"],
        paint: { "fill-color": PREVIEW_COLOR, "fill-opacity": 0.15 },
    },
    {
        id: `${COORDINATE_PREVIEW_SOURCE_ID}-line`,
        type: "line",
        source: COORDINATE_PREVIEW_SOURCE_ID,
        paint: {
            "line-color": PREVIEW_COLOR,
            "line-width": 2,
            "line-dasharray": [2, 2],
        },
    },
    {
        id: `${COORDINATE_PREVIEW_SOURCE_ID}-point`,
        type: "circle",
        source: COORDINATE_PREVIEW_SOURCE_ID,
        filter: ["in", ["geometry-type"], ["literal", ["Point", "MultiPoint"]]],
        paint: { "circle-radius": 5, "circle-color": PREVIEW_COLOR },
    },
];

export interface UseCoordinatePreviewReturn {
    focusedRowPosition: ComputedRef<Position | null>;
    followFocusedRow: () => void;
    followFocusedRowDebounced: () => void;
    fitToPreview: () => void;
}

export function useCoordinatePreview(
    context: MapContext,
    coordinateEditor: UseCoordinateEditorReturn,
    focusedRowIndex: Ref<number | null>,
): UseCoordinatePreviewReturn {
    const { map, fitToFeatures, showFeatureHighlight, clearFeatureHighlight } =
        context;
    const {
        editingFeature,
        kind,
        areAllRowsComplete,
        previewGeometry,
        getRowWgs84Position,
    } = coordinateEditor;

    let hasFittedDraft = false;

    const refreshPreviewDebounced = debounce(
        refreshPreview,
        PREVIEW_DEBOUNCE_MILLISECONDS,
    );
    const followFocusedRowDebounced = debounce(
        followFocusedRow,
        PREVIEW_DEBOUNCE_MILLISECONDS,
    );

    const focusedRowPosition = computed(() => {
        if (focusedRowIndex.value === null) {
            return null;
        }
        return getRowWgs84Position(focusedRowIndex.value);
    });

    watch(previewGeometry, refreshPreviewDebounced);

    watch(focusedRowPosition, (position) => {
        if (!position) {
            clearFeatureHighlight();
            return;
        }
        showFeatureHighlight([{ type: "Point", coordinates: position }]);
    });

    onUnmounted(() => {
        refreshPreviewDebounced.cancel();
        followFocusedRowDebounced.cancel();
        clearFeatureHighlight();
        removePreview();
    });

    function refreshPreview(geometry: Geometry | null): void {
        showPreview(geometry);

        if (!geometry || !areAllRowsComplete.value || kind.value === POINT) {
            hasFittedDraft = false;
            return;
        }
        if (editingFeature || hasFittedDraft) {
            return;
        }

        hasFittedDraft = true;
        followFocusedRowDebounced.cancel();
        fitToPreview();
    }

    function followFocusedRow(): void {
        if (!focusedRowPosition.value) {
            return;
        }

        const [longitude, latitude] = focusedRowPosition.value;
        map.value?.flyTo({
            center: [longitude, latitude],
            zoom: Math.max(map.value.getZoom(), VERTEX_FOCUS_ZOOM),
            essential: true,
        });
    }

    function fitToPreview(): void {
        if (!previewGeometry.value) {
            return;
        }
        fitToFeatures([
            {
                type: "Feature",
                properties: {},
                geometry: previewGeometry.value,
            },
        ]);
    }

    function showPreview(geometry: Geometry | null): void {
        if (!map.value) {
            return;
        }

        const geometries = geometry ? [geometry] : [];
        const previewData = geometriesToFeatureCollection(geometries);
        const previewSource = map.value.getSource<GeoJSONSource>(
            COORDINATE_PREVIEW_SOURCE_ID,
        );
        if (previewSource) {
            previewSource.setData(previewData);
            return;
        }

        map.value.addSource(COORDINATE_PREVIEW_SOURCE_ID, {
            type: "geojson",
            data: previewData,
        });
        for (const layer of PREVIEW_LAYERS) {
            map.value.addLayer(layer);
        }
    }

    function removePreview(): void {
        if (!map.value || !map.value.getSource(COORDINATE_PREVIEW_SOURCE_ID)) {
            return;
        }

        for (const layer of PREVIEW_LAYERS) {
            map.value.removeLayer(layer.id);
        }
        map.value.removeSource(COORDINATE_PREVIEW_SOURCE_ID);
    }

    return {
        focusedRowPosition,
        followFocusedRow,
        followFocusedRowDebounced,
        fitToPreview,
    };
}
